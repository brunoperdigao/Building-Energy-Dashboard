import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

GRID_COLOR = '#d1d1d1'
TEXT_COLOR = '#414141'
HUE_COLORS = ['steelblue', 'orange', 'seagreen', 'red']


pio.templates['new_template'] = go.layout.Template(
    layout_font= dict(
        color=TEXT_COLOR,
        family='Segoe UI',),
    layout_margin= dict(
        t=10,
        b=60,
        l=70,
        r=20,
        ),
    layout_xaxis= dict(
        gridcolor=GRID_COLOR,
        gridwidth=1,
        # showline=True,
        # linecolor=TEXT_COLOR,
        # linewidth=2,
        ),
    layout_yaxis = dict(
        gridcolor=GRID_COLOR,
        gridwidth=1,
        showline=True,
        linecolor=TEXT_COLOR,
        linewidth=1,
        ticksuffix="  ",
        ),
    layout_hovermode = 'x unified',
)
