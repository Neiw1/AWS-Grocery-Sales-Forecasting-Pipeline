import pandas as pd

df = pd.read_csv('engineered_test.csv')

data_to_cloud = df[df['date'] < '2017-08-10']
data_to_test = df[df['date'] > '2017-08-10']

drop_cols = ['sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7']
data_to_test = df.drop(columns=drop_cols)
data_to_test.to_csv("test_for_prediction.csv", index=False)