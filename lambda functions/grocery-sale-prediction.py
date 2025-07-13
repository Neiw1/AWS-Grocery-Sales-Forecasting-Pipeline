import boto3
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
import io
import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Bucket and key configurations
    input_bucket = "grocery-price-prediction-cleaned-data"
    input_key = "prices.csv"
    
    model_bucket = "grocery-price-prediction-cleaned-data"
    model_key = "models/model.txt"
    
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    output_bucket = "grocery-price-prediction-output"
    output_key = f"predictions_{ts}.csv"

    test_obj = s3.get_object(Bucket=input_bucket, Key=input_key)
    df_test = pd.read_csv(io.BytesIO(test_obj['Body'].read()))

    # ---- Label encode categorical columns ----
    cat_cols = ['onpromotion', 'family', 'city', 'state', 'type_x', 'promo_lag_1', 'promo_lag_7']
    for col in cat_cols:
        le = LabelEncoder()
        df_test[col] = le.fit_transform(df_test[col].astype(str))

    feature_cols = [
        'store_nbr', 'item_nbr', 'onpromotion', 'family', 'class', 'perishable',
        'city', 'state', 'type_x', 'cluster', 'transactions', 'dcoilwtico',
        'month', 'is_weekend', 'sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7'
    ]
    X_test = df_test[feature_cols].fillna(0)

    model_obj = s3.get_object(Bucket=model_bucket, Key=model_key)
    model_buffer = io.BytesIO(model_obj['Body'].read())
    model = lgb.Booster(model_str=model_buffer.read().decode("utf-8"))

    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    y_pred_original = np.expm1(y_pred)
    df_test['predicted_unit_sales'] = y_pred_original.clip(0)

    # ---- Convert to CSV and upload to output bucket ----
    output_csv = df_test[['id', 'predicted_unit_sales']].to_csv(index=False)
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=output_csv.encode('utf-8'),
        ContentType='text/csv'
    )

    return {
        "statusCode": 200,
        "message": f"Prediction saved to s3://{output_bucket}/{output_key}"
    }
