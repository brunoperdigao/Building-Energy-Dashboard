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
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import templates

pio.templates.default = "new_template"


# %%
df_historical = pd.read_feather("./2-year-historical-weather.feather")
df_historical.set_index('time', inplace=True)
df_historical.head(10)

# %%
# Reshape hourly data to daily avarage
df_historical = df_historical.resample("D").mean()
df_historical.head(10)


# %%
df_energy = pd.read_feather("./building-energy.feather")
df_energy.set_index('timestamp', inplace=True)
df_energy.head(10)

# %%
df_energy.info()

# %%
# Joining both dataframes
df_historical_plus_energy = df_energy.merge(df_historical, left_index=True, right_index=True)
df_historical_plus_energy.columns



# %%
# Plots with daily data
fig = make_subplots(rows=3, cols=1) 
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy.index,
            y=df_historical_plus_energy['value']
            ),
        row=1, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy.index,
            y=df_historical_plus_energy['temperature_2m']
            ),
        row=2, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy.index,
            y=df_historical_plus_energy['relativehumidity_2m']
            ),
        row=3, col=1
        )
# fig.update_layout(template="my_template")
fig.show()

# %%
# Plots with monthly data
df_historical_plus_energy_monthly = df_merge.resample('M').mean()
fig = make_subplots(rows=3, cols=1) 
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy_monthly.index,
            y=df_historical_plus_energy_monthly['value']
            ),
        row=1, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy_monthly.index,
            y=df_historical_plus_energy_monthly['temperature_2m']
            ),
        row=2, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_historical_plus_energy_monthly.index,
            y=df_historical_plus_energy_monthly['relativehumidity_2m']
            ),
        row=3, col=1
        )
fig.show()

# %%
df_current_weather = pd.read_feather('./current-weather.feather')
df_current_weather.set_index('time', inplace=True)
df_current_weather.head(10)

# %%
df_current_plus_energy = df_energy.merge(df_current_weather, left_index=True, right_index=True)
df_current_plus_energy.columns


# %%
# Plots with daily data
fig = make_subplots(rows=3, cols=1) 
fig.add_trace(
        go.Scatter(
            x=df_current_plus_energy.index,
            y=df_current_plus_energy['value']
            ),
        row=1, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_current_plus_energy.index,
            y=df_current_plus_energy['temperature_2m']
            ),
        row=2, col=1
        )
fig.add_trace(
        go.Scatter(
            x=df_current_plus_energy.index,
            y=df_current_plus_energy['relativehumidity_2m']
            ),
        row=3, col=1
        )
fig.show()


# %%


# %%


# %%


# %%


# %%



