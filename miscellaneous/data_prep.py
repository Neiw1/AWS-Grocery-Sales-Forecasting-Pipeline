import pandas as pd

df = pd.read_csv('engineered_test.csv')

df['store_item'] = df['store_nbr'].astype(str) + "#" + df['item_nbr'].astype(str)

data_to_cloud = df[(df['date'] < '2017-08-15') & (df['date'] > '2017-08-08')].copy()
data_to_test = df[df['date'] >= '2017-08-15'].copy()

drop_cols = ['sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7']
data_to_test = data_to_test.drop(columns=drop_cols)

cols_cloud = ['store_item'] + [col for col in data_to_cloud.columns if col != 'store_item']
data_to_cloud = data_to_cloud[cols_cloud]

cols_test = ['store_item'] + [col for col in data_to_test.columns if col != 'store_item']
data_to_test = data_to_test[cols_test]

data_to_cloud.to_csv("for_uploading.csv", index=False)
data_to_test.to_csv("test_for_prediction.csv", index=False)