import pandas as pd
from dash import Dash

import i18n

from src.data.loader import load_office_buildings, create_building_historical_dataframe, create_building_forecast_dataframe, create_building_energy_forecast_dataframe
from src.components.layout import create_layout

LOCALE = 'en'

app = Dash(__name__)
server = app.server

i18n.set('locale', LOCALE)
i18n.load_path.append('translations')

buildings_info, default_name = load_office_buildings()
df_historical = create_building_historical_dataframe(default_name)
df_forecast = create_building_forecast_dataframe(default_name)

mask = df_forecast['value'].notna()
energy_data_last_date = df_forecast[mask].index[-1]

app.title = i18n.t('general.app_title') 
app.layout = create_layout(app, df_historical, df_forecast, buildings_info)

def main():

    app.run_server(debug=True)


if __name__ == "__main__":
    main()




