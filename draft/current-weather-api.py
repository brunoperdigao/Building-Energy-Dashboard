# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
# ---

# %%
import pandas as pd
import plotly.express as px
import requests
from utils import store_feather_data


# %%
params = {
        "latitude":"60.19",
        "longitude":"24.94",
        "hourly": ["temperature_2m", "relativehumidity_2m"],
        "past_days": 30,
        "timezone": "auto",
        }
endpoint = "https://api.open-meteo.com/v1/forecast"
response = requests.get(endpoint, params=params)
response.json()['hourly'].keys()


# %%
response_dict = response.json()['hourly']
df = pd.DataFrame.from_dict(response_dict)
df.info()

# %%
df['time'] = pd.to_datetime(df['time'])
df.info()

# %%
today = "2022-08-18"
fig = px.line(df, x = 'time', y = 'temperature_2m')
fig.add_vline(x=today)
fig.show()

# %%
fig = px.line(df, x = 'time', y = 'relativehumidity_2m')
fig.add_vline(x=today)
fig.show()


# %%
df.head(5)

# %%
store_feather_data(df, "current-weather.feather")


# %%


# %%


# %%


# %%


# %%


# %%


# %%



