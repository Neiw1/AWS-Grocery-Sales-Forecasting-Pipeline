import boto3
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
import io
import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

def decimal_to_float(item):
    if isinstance(item, list):
        return [decimal_to_float(i) for i in item]
    elif isinstance(item, dict):
        return {k: decimal_to_float(v) for k, v in item.items()}
    elif isinstance(item, Decimal):
        return float(item)
    else:
        return item

def lambda_handler(event, context):
    model_bucket = "grocery-price-prediction-cleaned-data"
    model_key = "models/model.txt"
    
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")
    output_bucket = "grocery-price-prediction-output"
    output_key = f"predictions_{ts}.csv"

    table_name = "GroceryData"
    table = dynamodb.Table(table_name)

    items = []
    scan_kwargs = {}
    done = False
    start_key = None

    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

    items = [decimal_to_float(item) for item in items]
    df = pd.DataFrame(items)

    cat_cols = ['onpromotion', 'family', 'city', 'state', 'type_x', 'promo_lag_1', 'promo_lag_7']
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    feature_cols = [
        'store_nbr', 'item_nbr', 'onpromotion', 'family', 'class', 'perishable',
        'city', 'state', 'type_x', 'cluster', 'transactions', 'dcoilwtico',
        'month', 'is_weekend', 'sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7'
    ]
    X_test = df[feature_cols].fillna(0)

    model_obj = s3.get_object(Bucket=model_bucket, Key=model_key)
    model_buffer = io.BytesIO(model_obj['Body'].read())
    model = lgb.Booster(model_str=model_buffer.read().decode("utf-8"))

    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    y_pred_original = np.expm1(y_pred)
    df['predicted_unit_sales'] = y_pred_original.clip(0)

    # ---- Convert to CSV and upload to output bucket ----
    output_csv = df[['id', 'predicted_unit_sales']].to_csv(index=False)
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=output_csv.encode('utf-8'),
        ContentType='text/csv'
    )



    return {
        "statusCode": 200,
        "body": "Read {} records from DynamoDB successfully".format(len(df))
    }
