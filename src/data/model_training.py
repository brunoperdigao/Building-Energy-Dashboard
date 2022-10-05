import pandas as pd
import numpy as np
import pickle
import bz2file as bz2
from tqdm.auto import tqdm 
from sklearn import metrics
from statsmodels.tsa.api import VAR
from statsmodels.tsa.statespace.varmax import VARMAX
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

# import xgboost as  xgb

from darts import TimeSeries
from darts.models.forecasting.linear_regression_model import LinearRegressionModel
from darts.models.forecasting.regression_model import RegressionModel
from darts.models.forecasting.gradient_boosted_model import LightGBMModel

import plotly.express as px
import plotly.graph_objects as go
from src.data.loader import create_building_historical_dataframe, load_office_buildings, create_building_forecast_dataframe

buildings_info, default_name = load_office_buildings()

### Data prepataion
df_forecast = create_building_forecast_dataframe('091-004-0001-0012')
df_forecast = df_forecast.drop(columns=['reportingGroup', 'locationName', 'unit'])
df_forecast = df_forecast[df_forecast['value'].isna()]
df = create_building_historical_dataframe('091-004-0001-0012')
df = df.drop(columns=['reportingGroup', 'locationName', 'unit'])
df['day_of_year'] = df.index.dayofyear
df['day_of_week'] = df.index.dayofweek
df['month'] = df.index.month
df['year'] = df.index.year
df['weekend'] = (df.index.dayofweek >= 5).astype(int)

### Data visualization

fig = px.box(df, x='month', y='value')
fig.show()

fig = px.box(df, x='weekend', y='value')
fig.show()

fig = px.box(df, x='day_of_week', y='value')
fig.show()

fig = px.box(df, x='year', y='value')
fig.show()

### Removing outliers
df.loc[df.value > 1400, 'value'] = np.nan
df.loc[df.value < 300, 'value'] = np.nan
df = df.fillna(method='ffill')


### Train/Test Split

df_train = df.loc[df.index < "2022-04-01"]
df_test = df.loc[(df.index >= "2022-04-01") & (df.index < "2022-09-01")]

fig = go.Figure()
fig.add_trace(
        go.Scatter(x=df_train.index, y=df_train.value)
        )

fig.add_trace(
        go.Scatter(x=df_test.index, y=df_test.value)
        )

### Training with SVR
df_var = df[['value', 'temperature_2m', 'relativehumidity_2m']]

adf_energy = adfuller(df['value'])
print(f"p_value: {adf_energy[1]}")
if adf_energy[1] < 0.05:
    print("It is stationary")
else:
    print("It's not stationary")

adf_temperature = adfuller(df['temperature_2m'])
print(f"p_value: {adf_temperature[1]}")
if adf_temperature[1] < 0.05:
    print("It is stationary")
else:
    print("It's not stationary")

adf_humidity = adfuller(df['relativehumidity_2m'])
print(f"p_value: {adf_humidity[1]}")
if adf_humidity[1] < 0.05:
    print("It is stationary")
else:
    print("It's not stationary")

grangercausalitytests(df_var[['value', 'temperature_2m']], 4)
grangercausalitytests(df_var[['value', 'relativehumidity_2m']], 4)

model = VAR(df_var)
order = model.select_order(maxlags=20)
print(order.summary())

var_model = VARMAX(df_var, order=(15, 0), enforce_stationarity=True)
var_model_fit = var_model.fit(disp=True)
print(var_model_fit.summary())

train_df_var = df_var[:-30]
test_df_var = df_var[-30:]

n_forecast = 20
prediction = var_model_fit.get_prediction(start=len(train_df_var), end=len(train_df_var) + n_forecast)
prediction = prediction.predicted_mean

pred_test = prediction.merge(test_df_var['value'], how='inner', left_index = True, right_index = True)

fig = go.Figure()
fig.add_trace(
        go.Scatter(x=pred_test.index, y=pred_test.value_x)
        )

fig.add_trace(
        go.Scatter(x=pred_test.index, y=pred_test.value_y)
        )
fig.show()


rmse = np.sqrt(metrics.mean_squared_error(pred_test['value_y'], pred_test['value_x']))
r2 = metrics.r2_score(pred_test['value_y'], pred_test['value_x'])
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")

### Saving the model

with bz2.BZ2File('./src/data/model_energy_consunption' + '.pbz2', 'w') as f:
    pickle.dump(var_model_fit, f)

### Using Darts
new_df = pd.concat([df, df_forecast]) 
df_darts = new_df.copy()
df_darts_train = df_darts[:-90]
df_darts_test = df_darts[-90:]


ts_value = TimeSeries.from_series(df_darts_train['value'])
ts_temperature = TimeSeries.from_series(df_darts_train['temperature_2m'])
ts_humidity = TimeSeries.from_series(df_darts_train['relativehumidity_2m'])

ts_future_temperature = TimeSeries.from_series(df_darts['temperature_2m'])
ts_future_humidity = TimeSeries.from_series(df_darts['relativehumidity_2m'])

ts_future_temperature_predict = TimeSeries.from_series(df_darts['temperature_2m'])
ts_future_humidity_predict = TimeSeries.from_series(df_darts['relativehumidity_2m'])

darts_model = LightGBMModel(lags=15, lags_past_covariates=15, lags_future_covariates=[1], output_chunk_length=90)
darts_model = darts_model.fit(ts_value, 
        past_covariates=ts_temperature.stack(ts_humidity),
        future_covariates=ts_future_temperature.stack(ts_future_humidity))

prediction = darts_model.predict(90, future_covariates=ts_future_temperature.stack(ts_future_humidity))

result = pd.concat([df_darts_test['value'], prediction.pd_series()],axis=1, join='inner')

fig = px.line(result)
fig.show()
