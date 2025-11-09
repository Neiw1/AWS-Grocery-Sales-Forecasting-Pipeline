import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
import os

cwd = os.getcwd()
data_folder = os.path.join(cwd, "sales_forecasting_data")

df_test = pd.read_csv(os.path.join(data_folder, "engineered_test.csv"))

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

model = lgb.Booster(model_file= (os.path.join(cwd, "model.txt")))

y_pred = model.predict(X_test, num_iteration=model.best_iteration)

y_pred_original = np.expm1(y_pred)

df_test['predicted_unit_sales'] = y_pred_original.clip(0)
df_test[['id', 'predicted_unit_sales']].to_csv('predictions.csv', index=False)