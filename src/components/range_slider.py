import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

def render(app: Dash, df: pd.DataFrame) -> list:
    # if not df:
    #     return ''
    start = df.index[0] 
    end = df.index[-1] 
    value = [start, end]
    return dcc.DatePickerRange(
            min_date_allowed=start,
            start_date=start,
            max_date_allowed=end,
            end_date=end,
            id='range-slider'
            )
