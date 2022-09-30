import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

def render(app: Dash, buildings_info: list) -> list:
    names_list = [x[0] for x in buildings_info]
    names_edit = []
    for name in names_list:
        if len(name) > 35:
            edited_name = name[:35] + '...'
            names_edit.append(edited_name)
        else:
            names_edit.append(name)
    return dcc.Dropdown(names_edit, names_edit[2], id='dd-buildings')
