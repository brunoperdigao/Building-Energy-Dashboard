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
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from utils import store_feather_data

# %%
endpoint_properties = "https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/List"
response_properties = requests.get(endpoint_properties)
response_properties

# %%
len(response_properties.json())

# %% [markdown]
# Fazer uma busca pelo tipo de edifício. Por enquanto focaremos em edifícios de escritório.

# %%
endpoint_offices = "https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/Search"
params_offices = {
        'SearchString': 'office',
        'SearchFromRecord': 'BuildingType',
        }
response_offices = requests.get(endpoint_offices, params=params_offices)
response_offices

# %%
len(response_offices.json())

# %%
property_code = response_offices.json()[1]['propertyCode']
print(property_code)



# %% [markdown]
# Fazer busca pelos dados energéticos de um edifício a partir do seu "property code". O intervalo de tempo e tipo (diário) é o mesmo coletado na api de dados climáticos

# %%
endpoint_energy = "https://helsinki-openapi.nuuka.cloud/api/v1/EnergyData/Daily/ListByProperty"

params_energy = {
        'Record': 'PropertyCode',
        'SearchString': property_code,
        'ReportingGroup': 'Electricity',
        'StartTime': '2020-01-01',
        'EndTime': '2022-08-01',
        }
response_energy = requests.get(endpoint_energy, params=params_energy)
response_energy

# %%
df = pd.DataFrame.from_dict(response_energy.json())
df.info()

# %%
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.info()

# %%
fig = px.line(df, x='timestamp', y='value')
fig.show()

# %%
store_feather_data(df, "building-energy.feather")

