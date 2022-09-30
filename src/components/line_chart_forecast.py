import pandas as pd
import numpy as np
import i18n
import pickle
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import assets.template
from assets.template import HUE_COLORS

from src.data.loader import load_forecast_weather_data, load_historical_weather_data, create_building_forecast_dataframe, load_office_buildings, create_building_energy_forecast_dataframe

pio.templates.default = "new_template"

def render(app: Dash, df: pd.DataFrame, buildings_info: list) -> html.Div:
    @app.callback(
        Output('plot-forecast', "children"),
        Input('interval', 'n_intervals'),
        Input('dd-buildings', 'value'),
           )
    def update_line_chart(n_intervals: int, value: str) -> html.Div:
        ### UPDATE DF WITH DROPDOWN VALUE
        if value:
            for item in buildings_info:
                if item[0] == value:
                    property_code = item[-1] # property code is always last but not always second, because some buildings hame more then one location name
                    df = create_building_forecast_dataframe(property_code)
                    break 
        if df.shape[0] == 0:
            return html.Div(i18n.t('general.missing_data'))
        
        mask = df['value'].notna()
        energy_data_last_date = df[mask].index[-1]
        print(energy_data_last_date)
        print(type(energy_data_last_date))
        

        def split_dataframe(x, forecast=False):
            if forecast:
                if x in df[df.index <= energy_data_last_date].values:
                    return np.nan
                else:
                    return x
            else:
                if x in df[df.index > energy_data_last_date].values:
                    return np.nan
                else:
                    return x
        
        #SPLITING TEMPERATURE DATAFRAME
        df_temperature_last_days = df.copy()
        df_temperature_last_days['temperature_2m'] = df['temperature_2m'].apply(split_dataframe)

        df_temperature_forecast = df.copy()
        df_temperature_forecast['temperature_2m'] = df['temperature_2m'].apply(split_dataframe, forecast=True)

        #SPLITING HUMIDITY DATAFRAME
        df_humidity_last_days = df.copy()
        df_humidity_last_days['relativehumidity_2m'] = df['relativehumidity_2m'].apply(split_dataframe)

        df_humidity_forecast = df.copy()
        df_humidity_forecast['relativehumidity_2m'] = df['relativehumidity_2m'].apply(split_dataframe, forecast=True)

        print("TESTE")

        #CREATING ENERGY FORECAST DATAFRAME
        df_energy_prediction = create_building_energy_forecast_dataframe(energy_data_last_date, 9)
        

        fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.15) 

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['value'],
                name=i18n.t('general.energy_past'),
                line=dict(color=HUE_COLORS[0])
                ),
            row=1, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df_energy_prediction.index,
                y=df_energy_prediction['value'],
                name=i18n.t('general.energy_forecast'),
                mode='lines',
                line=dict(dash='dash', color=HUE_COLORS[0])
                ),
            row=1, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df_temperature_last_days['temperature_2m'],
                name=i18n.t('general.temperature_past'),
                line=dict(color=HUE_COLORS[1])
                ),
            row=2, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df_temperature_forecast['temperature_2m'],
                name=i18n.t('general.temperature_forecast'),
                line=dict(dash='dash', color=HUE_COLORS[1])
                ),
            row=2, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df_humidity_last_days['relativehumidity_2m'],
                name=i18n.t('general.humidity_past'),
                line=dict(color=HUE_COLORS[2])
                ),
            row=3, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df_humidity_forecast['relativehumidity_2m'],
                name=i18n.t('general.humidity_forecast'),
                line=dict(dash='dash', color=HUE_COLORS[2])
                ),
            row=3, col=1,
            )
        
        fig.add_vline(energy_data_last_date, line_width=2, line_color=HUE_COLORS[3])
        fig.update_layout(legend_title=i18n.t('general.legend_title'))
        
        #Axis Titles
        fig['layout']['yaxis']['title'] = "Kw/h"
        fig['layout']['yaxis2']['title'] = "°C"
        fig['layout']['yaxis3']['title'] = "%"
        fig['layout']['xaxis3']['title'] = i18n.t('general.timeline') 

        return html.Div(dcc.Graph(figure=fig, config=dict(displayModeBar=False)), id='line_chart_forecast') 
    
