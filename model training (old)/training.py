import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import lightgbm as lgb
import os

cwd = os.getcwd()
data_folder = os.path.join(cwd, "sales_forecasting_data")

df_train = pd.read_csv(os.path.join(data_folder, "engineered_train.csv"))
df_val = pd.read_csv(os.path.join(data_folder, "engineered_validation.csv"))

df_train['unit_sales'] = df_train['unit_sales'].clip(lower=0).apply(np.log1p)
df_val['unit_sales'] = df_val['unit_sales'].clip(lower=0).apply(np.log1p)

cat_cols = ['onpromotion', 'family', 'city', 'state', 'type_x', 'promo_lag_1', 'promo_lag_7']

label_encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df_train[col] = le.fit_transform(df_train[col].astype(str))
    df_val[col] = le.transform(df_val[col].astype(str))
    label_encoders[col] = le

feature_cols = [
    'store_nbr', 'item_nbr', 'onpromotion', 'family', 'class', 'perishable',
    'city', 'state', 'type_x', 'cluster', 'transactions', 'dcoilwtico',
    'month', 'is_weekend', 'sale_lag_1', 'sale_lag_7', 'promo_lag_1', 'promo_lag_7'
]

X_train = df_train[feature_cols]
y_train = df_train['unit_sales']
X_val = df_val[feature_cols]
y_val = df_val['unit_sales']

lgb_train = lgb.Dataset(X_train, y_train, categorical_feature=cat_cols, free_raw_data=False)
lgb_val = lgb.Dataset(X_val, y_val, reference=lgb_train, categorical_feature=cat_cols, free_raw_data=False)

params = {
    'objective': 'regression',
    'metric': 'rmse',
    'learning_rate': 0.03,
    'num_leaves': 80,
    'verbose': -1,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.7,
    'bagging_freq': 1,
    'seed': 42
}

model = lgb.train(
    params,
    lgb_train,
    num_boost_round=1000,
    valid_sets=[lgb_train, lgb_val],
    valid_names=['train', 'valid'],
)

y_pred = model.predict(X_val, num_iteration=model.best_iteration)
rmse = mean_squared_error(y_val, y_pred, squared=False)
print(f"Validation RMSE: {rmse:.5f}")

model.save_model('lgb_model.txt')