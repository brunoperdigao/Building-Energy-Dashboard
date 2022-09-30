import pandas as pd
import i18n
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from src.components import line_chart_historical, line_chart_forecast, range_slider, dropdown_buildings, general_stats

def create_layout(app: Dash,
    df_historical: pd.DataFrame,
    df_forecast: pd.DataFrame,
    buildings_info: list) -> html.Div:
    return html.Div(
        id='main',
        children=[
            html.Div(
                id='navbar-wrapper',
                children=[
                    dcc.Interval(id='interval', interval=1000*500, n_intervals=0),
                    html.H1(app.title),
                    html.Hr(),
                    html.Div(
                        id='dd-buildings-container',
                        children=[html.H4(i18n.t('general.dd_title')), dropdown_buildings.render(app, buildings_info)],
                        ),
                    html.Div(
                        id='range-slider-container',
                        children=[html.H4(i18n.t('general.daterange_title')), range_slider.render(app, df_historical)],
                        ),
                    html.Hr(),
                    html.Div(
                        id='energy-info',
                        children=[
                            general_stats.render(app, df_historical, buildings_info),
                        ]),
                    html.Hr(),
                    html.Div(
                        id='description',
                        children=[
                            html.H3(i18n.t('general.description_title')),
                            dcc.Markdown(i18n.t('general.description')),
                            ]
                        ),
                    ]),
            html.Div(
                id='main-div',
                children=[
                    html.H2(i18n.t('general.plot_historical_title')),
                    html.Div(
                        id='plot-historical',
                        children= [line_chart_historical.render(app, df_historical, buildings_info)],
                        ),
                    html.H2(i18n.t('general.plot_forecast_title')),
                    html.Div(
                        id='plot-forecast',
                        children= [line_chart_forecast.render(app, df_forecast, buildings_info)],
                        ),
                    ],
                ),
        ],
    )
