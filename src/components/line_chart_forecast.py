import pandas as pd
import numpy as np
import i18n
import os
from dash import Dash, html, dcc, CeleryManager
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import assets.template
from assets.template import HUE_COLORS

from src.data.loader import load_forecast_weather_data, load_historical_weather_data, create_building_forecast_dataframe, create_building_historical_dataframe, load_office_buildings, create_building_energy_forecast_dataframe

pio.templates.default = "new_template"

def render(app: Dash,
        df_forecast: pd.DataFrame,
        df_historical: pd.DataFrame,
        buildings_info: list) -> html.Div:
    @app.callback(
        Output('plot-forecast', "children"),
        Input('interval', 'n_intervals'),
        Input('dd-buildings', 'value'),
           )
    def update_line_chart(n_intervals: int, dd_value: str) -> html.Div:
        local_df_forecast = df_forecast.copy()
        local_df_historical = df_historical.copy()
        
        ### UPDATE DF WITH DROPDOWN VALUE
        if dd_value:
            for item in buildings_info:
                found_match = False
                print("<>", item[0][:10],"<>", dd_value[:10])
                if item[0][:10] == dd_value[:10]: #check for the first 10 letters
                    property_code = item[-1] # property code is always last but not always second, because some buildings hame more then one location name
                    local_df_forecast = create_building_forecast_dataframe(property_code)
                    local_df_historical = create_building_historical_dataframe(property_code)
                    found_match = True
                    break
            if not found_match:
                return html.Div(i18n.t('general.missing_data'))
                
        if local_df_forecast.shape[0] == 0:
            return html.Div(i18n.t('general.missing_data'))
        
        mask = local_df_forecast['value'].notna()
        energy_data_last_date = local_df_forecast[mask].index[-1]
        

        def split_dataframe(x, forecast=False):
            if forecast:
                if x in local_df_forecast[local_df_forecast.index <= energy_data_last_date].values:
                    return np.nan
                else:
                    return x
            else:
                if x in local_df_forecast[local_df_forecast.index > energy_data_last_date].values:
                    return np.nan
                else:
                    return x
        
        #SPLITING TEMPERATURE DATAFRAME
        df_temperature_last_days = local_df_forecast.copy()
        df_temperature_last_days['temperature_2m'] = local_df_forecast['temperature_2m'].apply(split_dataframe)

        df_temperature_forecast = local_df_forecast.copy()
        df_temperature_forecast['temperature_2m'] = local_df_forecast['temperature_2m'].apply(split_dataframe, forecast=True)

        #SPLITING HUMIDITY DATAFRAME
        df_humidity_last_days = local_df_forecast.copy()
        df_humidity_last_days['relativehumidity_2m'] = local_df_forecast['relativehumidity_2m'].apply(split_dataframe)

        df_humidity_forecast = local_df_forecast.copy()
        df_humidity_forecast['relativehumidity_2m'] = local_df_forecast['relativehumidity_2m'].apply(split_dataframe, forecast=True)
        
        #GETTING THE ENERGY PREDICTION
        df_energy_predict = create_building_energy_forecast_dataframe(20, local_df_historical, local_df_forecast)
        print("!ENERGY PREDICT!", df_energy_predict.head(5))

        

        fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.15) 

        fig.add_trace(
            go.Scatter(
                x=local_df_forecast.index,
                y=local_df_forecast['value'],
                name=i18n.t('general.energy_past'),
                line=dict(color=HUE_COLORS[0])
                ),
            row=1, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=df_energy_predict.index,
                y=df_energy_predict['value'],
                name=i18n.t('general.energy_forecast'),
                mode='lines',
                line=dict(dash='dash', color=HUE_COLORS[0])
                ),
            row=1, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=local_df_forecast.index,
                y=df_temperature_last_days['temperature_2m'],
                name=i18n.t('general.temperature_past'),
                line=dict(color=HUE_COLORS[1])
                ),
            row=2, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=local_df_forecast.index,
                y=df_temperature_forecast['temperature_2m'],
                name=i18n.t('general.temperature_forecast'),
                line=dict(dash='dash', color=HUE_COLORS[1])
                ),
            row=2, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=local_df_forecast.index,
                y=df_humidity_last_days['relativehumidity_2m'],
                name=i18n.t('general.humidity_past'),
                line=dict(color=HUE_COLORS[2])
                ),
            row=3, col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=local_df_forecast.index,
                y=df_humidity_forecast['relativehumidity_2m'],
                name=i18n.t('general.humidity_forecast'),
                line=dict(dash='dash', color=HUE_COLORS[2])
                ),
            row=3, col=1,
            )
        
        fig.add_vline(energy_data_last_date, line_width=2, line_color=HUE_COLORS[3])
        fig.update_layout(legend_title=i18n.t('general.legend_title'),
                          margin=dict(t=30),
                          title_text=f"Building location: {dd_value}")
        
        #Axis Titles
        fig['layout']['yaxis']['title'] = "Kw/h"
        fig['layout']['yaxis2']['title'] = "°C"
        fig['layout']['yaxis3']['title'] = "%"
        fig['layout']['xaxis3']['title'] = i18n.t('general.timeline') 

        return html.Div(dcc.Graph(figure=fig, config=dict(displayModeBar=False)), id='line_chart_forecast') 
    
