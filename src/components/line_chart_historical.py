import pandas as pd
import i18n
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import assets.template
from assets.template import HUE_COLORS

from src.data.loader import load_forecast_weather_data, load_historical_weather_data, create_building_historical_dataframe, load_office_buildings

pio.templates.default = "new_template"

def render(app: Dash,
           df_historical: pd.DataFrame,
           buildings_info: list) -> html.Div:
    @app.callback(
        Output('plot-historical', "children"),
        Input('interval', 'n_intervals'),
        Input('dd-buildings', 'value'),
        Input('range-slider', 'start_date'),
        Input('range-slider', 'end_date'),
           )
    def update_line_chart(n_intervals: int, value: str, start: str, end: str) -> html.Div:
        local_df = df_historical.copy()
        ### UPDATE DF WITH DROPDOWN VALUE
        if value:
            for item in buildings_info:
                found_match = False
                if item[0][:10] == value[:10]: # check for the first 10 letters
                    property_code = item[-1] # property code is always last but not always second, becaus some buildings hame more then one location name
                    local_df = create_building_historical_dataframe(property_code)
                    found_match = True
                    break
            if not found_match:
                return html.Div(i18n.t('general.missing_data'))
                
        if local_df.shape[0] == 0:
            return html.Div(i18n.t('general.missing_data'))
        
        filtered_df = local_df[(local_df.index > start) & (local_df.index < end)]
        # print(">>>", local_df.index)
        # print(start, end)
        fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.15) 
        
        fig.add_trace(
            go.Scatter(
                x=filtered_df.index,
                y=filtered_df['value'],
                name=i18n.t('general.energy_hist'),
                line=dict(color=HUE_COLORS[0]),
                ),
            row=1, col=1
            )
        
        fig.add_trace(
            go.Scatter(
                x=filtered_df.index,
                y=filtered_df['temperature_2m'],
                name=i18n.t('general.temperature_hist'),
                line=dict(color=HUE_COLORS[1]),
                ),
            row=2, col=1
            )
        
        fig.add_trace(
            go.Scatter(
                x=filtered_df.index,
                y=filtered_df['relativehumidity_2m'],
                name=i18n.t('general.humidity_hist'),
                line=dict(color=HUE_COLORS[2]),
                ),
            row=3, col=1
            )

        fig.update_layout(legend_title=i18n.t('general.legend_title'))

        #Axis Titles
        fig['layout']['yaxis']['title'] = "Kw/h"
        fig['layout']['yaxis2']['title'] = "°C"
        fig['layout']['yaxis3']['title'] = "%"
        fig['layout']['xaxis3']['title'] = i18n.t('general.timeline') 
        return html.Div(dcc.Graph(figure=fig, config=dict(displayModeBar=False)), id='line_chart_historical') 
