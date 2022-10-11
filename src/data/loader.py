import pandas as pd
import numpy as np
import pickle
import bz2file as bz2
import requests
from datetime import date
from typing import Tuple
from dash.dependencies import Input, Output


TODAY = str(date.today())

def load_forecast_weather_data(past_days: int = 15) -> pd.DataFrame:
    params = {
        "latitude":"60.19",
        "longitude":"24.94",
        "hourly": ["temperature_2m", "relativehumidity_2m"],
        "past_days": past_days,
        "timezone": "auto",
        }
    endpoint = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(endpoint, params=params)
    response.json()['hourly'].keys()


    response_dict = response.json()['hourly']
    df = pd.DataFrame.from_dict(response_dict)
    df['time'] = pd.to_datetime(df['time'])
    df.rename(columns={'time': 'timestamp'}, inplace=True)
    df.set_index(['timestamp'], inplace=True)
    df = df.resample('D').mean()
    
    return df 

def load_historical_weather_data() -> pd.DataFrame:
    params = {
        "latitude":"60.19",
        "longitude":"24.94",
        "start_date":"2020-01-01",
        "end_date":TODAY,
        "hourly": ["temperature_2m", "relativehumidity_2m"],
        "timezone": "auto",
        }
    endpoint = "https://archive-api.open-meteo.com/v1/era5"
    response = requests.get(endpoint, params=params)
    response.json()['hourly'].keys()

    response_dict = response.json()['hourly']
    df = pd.DataFrame.from_dict(response_dict)
    df['time'] = pd.to_datetime(df['time'])
    df.rename(columns={'time': 'timestamp'}, inplace=True)
    df.set_index(['timestamp'], inplace=True)
    df = df.resample('D').mean()
    
    return df 

def load_office_buildings() -> Tuple[list, str]:
    
    endpoint_offices = "https://helsinki-openapi.nuuka.cloud/api/v1.0/Property/Search"
    params_offices = {
            'SearchString': 'office',
            'SearchFromRecord': 'BuildingType',
            }
    response_offices = requests.get(endpoint_offices, params=params_offices)

    # Cleaning the nested keys
    offices_list = response_offices.json()
    to_exclude = ['reportingGroups', 'buildings']
    new_list = []
    for item in offices_list:
        new_item = {key: item[key] for key in item.keys() if key not in to_exclude}
        new_list.append(new_item)
    df = pd.DataFrame.from_records(new_list)
    
    buildings_info = list(df[['locationName', 'propertyCode']].values)
    property_code = buildings_info[2][-1] # property code is always last but not always second, becaus some buildings hame more then one location name 
    
    return buildings_info, property_code 


def load_energy_data(property_code: str) -> pd.DataFrame:
    endpoint_energy = "https://helsinki-openapi.nuuka.cloud/api/v1/EnergyData/Daily/ListByProperty"

    params_energy = {
            'Record': 'propertyCode',
            'SearchString': property_code,
            'ReportingGroup': 'Electricity',
            'StartTime': '2020-01-01',
            'EndTime': TODAY,
            }
    response_energy = requests.get(endpoint_energy, params=params_energy)
    print("ENERGY RESPONSE", response_energy.status_code)

    if response_energy.status_code != 200:
        return pd.DataFrame()

    
    df = pd.DataFrame.from_dict(response_energy.json())

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index(['timestamp'], inplace=True)
    
    return df


def create_building_historical_dataframe(property_code: str) -> pd.DataFrame:
    
    df_energy = load_energy_data(property_code)
    if df_energy.shape[0] == 0:
        return df_energy
    
    df_historical_weather = load_historical_weather_data()

    df_merge = df_energy.merge(df_historical_weather, left_index=True, right_index=True)
    return df_merge 

def create_building_forecast_dataframe(property_code:str) -> pd.DataFrame:
    
    df_energy = load_energy_data(property_code)
    if df_energy.shape[0] == 0:
        return df_energy

    df_forecast_weather = load_forecast_weather_data()
    
    # df_merge = df_forecast_weather.merge(df_energy, how='outer', left_index=True, right_index=True)
    df_merge = df_forecast_weather.merge(df_energy, how='left', on='timestamp')

    return df_merge

def create_building_energy_forecast_dataframe(n_days_to_predict: int,
                                              df_historical: pd.DataFrame,
                                              df_forecast: pd.DataFrame) -> pd.DataFrame:

    # Creating future covariates TimeSeries
    df_hist_weather = df_historical.drop(columns={'reportingGroup', 'locationName', 'unit'})
    df_fore_weather = df_forecast.drop(columns={'reportingGroup', 'locationName', 'unit'})

    temperature_hist = df_hist_weather['temperature_2m']
    temperature_fore = df_fore_weather['temperature_2m']
    temperature_all = temperature_hist.combine_first(temperature_fore)


    humidity_hist = df_hist_weather['relativehumidity_2m']
    humidity_fore = df_fore_weather['relativehumidity_2m']
    humidity_all = humidity_hist.combine_first(humidity_fore)

    df_all_weather = pd.concat([temperature_all, humidity_all], axis=1)
    df_all_weather

    df_all_weather['weekend'] = (df_all_weather.index.dayofweek >= 5).astype(int)
    df_all_weather['month'] = df_all_weather.index.month

    df_all_weather = df_all_weather.reset_index()

    df_all_weather = df_all_weather.to_json()
    
    # Creating the building TimeSeries
    df_building = df_historical.drop(columns={'reportingGroup', 'locationName', 'unit', 'temperature_2m', 'relativehumidity_2m'})
    df_building = df_building.reset_index()
    df_building = df_building.to_json()


    # Making the request to the model api
    params = {
        "n_days_to_predict": n_days_to_predict,
        "json_fut_cov": df_all_weather,
        "json_building": df_building
        }
    endpoint_model = 'https://building-energy-ml-api.onrender.com/prediction/'
    response = requests.post(endpoint_model, json=params)
    print("API RESPONSE", response.status_code)
    if response:
        df_predict = pd.read_json(response.json())
    else:
        df_predict = pd.DataFrame()
        print('vazio')
        
    return df_predict
