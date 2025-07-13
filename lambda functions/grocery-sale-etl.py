import json
import boto3
import pandas as pd
from io import StringIO
import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    
    bucket = 'grocery-price-prediction-raw-data'
    key = 'prices.csv'
    
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')
    
    df = pd.read_csv(StringIO(data))

    # Data Cleaning
    df = df.drop(columns=['id'])
    if 'type_y' in df.columns:
        df['holiday'] = df['type_y'] == 'Holiday'
        df = df.drop(columns=['type_y'])
    else:
        df['holiday'] = False

    df = df.sort_values(by='date')

    df['dcoilwtico'] = df['dcoilwtico'].fillna(method='bfill')

    df['onpromotion'] = df['onpromotion'].fillna(False)
    df['transactions'] = df['transactions'].fillna(0)


    # Feature Engineering
    df.sort_values(['store_nbr', 'item_nbr', 'date'], inplace=True)
    df['date'] = pd.to_datetime(df['date'])

    df['dow'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month

    df = df.drop('holiday', axis=1)
    df['is_weekend'] = df['dow'].isin([5, 6]).astype(int)
    df = df.drop('dow', axis=1)

    df['sale_lag_1'] = df.groupby(['store_nbr', 'item_nbr'])['unit_sales'].shift(1)
    df['sale_lag_7'] = df.groupby(['store_nbr', 'item_nbr'])['unit_sales'].shift(7)

    df['promo_lag_1'] = df.groupby(['store_nbr', 'item_nbr'])['onpromotion'].shift(1)
    df['promo_lag_7'] = df.groupby(['store_nbr', 'item_nbr'])['onpromotion'].shift(7)

    lag_cols = ['sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7']

    for col in lag_cols:
        df[col] = df[col].fillna(0)

    df.dropna(subset=lag_cols, inplace=True)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    output_bucket = 'grocery-price-prediction-cleaned-data'
    pred_key = 'prices.csv'
    s3.put_object(Bucket=output_bucket, Key=pred_key, Body=csv_buffer.getvalue())
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Prediction saved to {pred_key}')
    }