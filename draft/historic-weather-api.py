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
#   kernelspec:
#     display_name: ambiente_virtual
#     language: python
#     name: ambiente_virtual
# ---

# %%
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from utils import store_feather_data

# %%
params = {
        "latitude":"60.19",
        "longitude":"24.94",
        "start_date":"2020-01-01",
        "end_date":"2022-08-01",
        "hourly": ["temperature_2m", "relativehumidity_2m"],
        "timezone": "auto",
        }
endpoint = "https://archive-api.open-meteo.com/v1/era5"
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
fig = px.line(df, x = 'time', y = 'temperature_2m')
fig.show()

# %%
fig = px.line(df, x = 'time', y = 'relativehumidity_2m')
fig.show()


# %%
df.head(5)

# %%
store_feather_data(df, "2-year-historical-weather.feather")

# %%
