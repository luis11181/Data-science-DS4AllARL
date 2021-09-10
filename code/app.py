import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Create the app
external_stylesheets = [dbc.themes.BOOTSTRAP, 'assets/styles.css']

request_path_prefix = None

app = dash.Dash(__name__, suppress_callback_exceptions=True,
                requests_pathname_prefix=request_path_prefix,
                external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])

app.title = "Positiva Analytics: Understanding models!"


#server = app.server



