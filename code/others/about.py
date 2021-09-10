import os
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

#####################################################################################
"""TITULO"""
titulo = html.H2(' ABOUT US ')


#####################################################################################
about = '/assets/about.png'

foto = html.Img(src=about, style={"width":"70%"}, className='center')

#####################################################################################

"""Layout"""


layout = html.Div(
    [titulo,
    foto ], className='center'
)