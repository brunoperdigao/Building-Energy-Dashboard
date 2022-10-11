import pandas as pd
import i18n
import datetime 
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

from src.data.loader import create_building_historical_dataframe

TODAY = datetime.date.today()
YEAR = datetime.timedelta(365)
MONTH = datetime.timedelta(30)


def render(app: Dash, df_historical: pd.DataFrame, buildings_info: list) -> dcc.Markdown:
    @app.callback(
            Output('energy-info', 'children'),
            Input('dd-buildings', 'value'),
            )
    def update_stats_summary(value: str) -> dcc.Markdown:
        local_df = df_historical.copy()
        
        ### UPDATE DF WITH DROPDOWN VALUE
        if value:
            for item in buildings_info:
                if item[0] == value:
                    property_code = item[-1] # property code is always last but not always second, becaus some buildings hame more then one location name
                    local_df = create_building_historical_dataframe(property_code)
                    break 
        if local_df.shape[0] == 0:
            return html.Div("The data is missing for this building")

        
        year_range = str(TODAY - YEAR)
        year_df = local_df[local_df.index > year_range]
        year_sum = year_df['value'].sum()
        year_average = year_df['value'].mean()

        month_range = str(TODAY - MONTH)
        month_df = local_df[local_df.index > month_range]
        month_sum = month_df['value'].sum()
        month_average = month_df['value'].mean()

        stats_year = i18n.t('general.stats_year').format(year_sum=year_sum, year_average=year_average)
        stats_month = i18n.t('general.stats_month').format(month_sum=month_sum, month_average=month_average)

        return [html.H3(i18n.t('general.stats_title')),
                html.H4(i18n.t('general.stats_year_title')),
                dcc.Markdown(stats_year),
                dcc.Markdown('''

                    &nbsp
                    
                    '''),
                html.H4(i18n.t('general.stats_month_title')),
                dcc.Markdown(stats_month),
                ]


