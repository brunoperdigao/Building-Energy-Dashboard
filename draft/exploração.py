# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: 'Python 3.10.0 (''ambiente-virtual'': venv)'
#     language: python
#     name: python3
# ---

# %%
import numpy as np
import pandas as pd
import plotly.express as px
import requests

# %%
endpoint_properties = "https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/List"
response_properties = requests.get(endpoint_properties)
response_properties

# %%
response_properties.json()[5]

# %%
counter = 0
size_of_data = 10
data_list = []
for item in response_properties.json():
    item_to_append = item['locationName'].split(',')[0]
    data_list.append(item_to_append)
    counter += 1
    if counter > size_of_data:
        break
data_list
    

# %%
building_list = []
endpoint_search = "https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/Search"

for item in data_list:
    params_search = {
        'SearchFromRecord': 'locationName',
        'SearchString': item
    }
    response_search = requests.get(endpoint_search, params=params_search)
    building_list.append(response_search.json())
building_list

# %%
keys_to_search = ['locationName','yearOfIntroduction', 'purposeOfUse', 'totalArea', 'buildingType', 'reportingGroups']
# {key: value for key, value in building_list[0][0] if key in keys_to_search}
for item in building_list:
    
    for key, value in item[0].items():
        if key in keys_to_search:
            print(key,": ", value)
    print("")

# %% [markdown]
# ## Trabalhando com 1 item

# %%
if building_list[14][0]['locationName'] == '1528 Apollon yhteiskoulu':
    print('deu certo')


# %%
location_name = '1610 Laakavuoren korttelitalo/a-a/Lpk'

def get_item_by_location (building_list, location):
    for item in building_list:
        if item[0]['locationName'] == location:
            return item[0]
        

building = get_item_by_location(building_list, location_name)
building



# %%
params_energy = {
    'Record': 'locationName',
    'SearchString': location_name,
    'ReportingGroup': 'Electricity',
    'StartTime': '2020-01-01',
    'EndTime': '2022-08-01',
}
endpoint_energy = "https://helsinki-openapi.nuuka.cloud/api/v1/EnergyData/Daily/ListByProperty"
response_energy = requests.get(endpoint_energy, params=params_energy)
response_energy.json()

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
test_of_creating_a_new_cell = True
