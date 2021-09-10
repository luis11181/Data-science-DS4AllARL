import os
import dash
import pandas as pd
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

from app import app
from analysis import description, main_menu, reasons
from forecast import model_output
from others import about


#####################################################################################
"""Navbar"""
LOGO = "/assets/positiva_logo.svg"
forecast_icon = '/assets/icons/crystal-ball-envision-future-forecast-svgrepo-com.svg'
graph_icon = '/assets/icons/graph-svgrepo-com.svg'
about_us_icon = '/assets/icons/about-us-svgrepo-com.svg'
reasons_icon = '/assets/icons/customer-reviews-svgrepo-com.svg'


search_bar = [
    dbc.Row(
        [
            dbc.Col(
                dbc.NavLink([html.Img(src=graph_icon, className="menu_icon"), " DATA EXPLORATION"], href="/analysis/description", className="ml-2, navitem", n_clicks=0
                            ),
                width="auto"
            ),

        ],
        no_gutters=True,
        className="mt-3 mt-md-0",
        align="center",
    ),
    dbc.Row(
        [
            dbc.Col(
                dbc.NavLink([html.Img(src=reasons_icon, className="menu_icon"), " REASONS"], href="/analysis/reasons", className="ml-2, navitem", n_clicks=0
                            ),
                width="auto"
            ),

        ],

        no_gutters=True,
        className="mt-3 mt-md-0",
        align="center",
    ),
    dbc.Row(
        [
            dbc.Col(
                dbc.NavLink([html.Img(src=forecast_icon, className="menu_icon"), " FORECAST"], href="/forecast/model_output", className="ml-2, navitem", n_clicks=0
                            ),
                width="auto"
            ),

        ],

        no_gutters=True,
        className=" mt-3 mt-md-0",
        align="center",
    ),
    dbc.Row(
        [dbc.Col(
            dbc.NavLink([html.Img(src=about_us_icon, className="menu_icon"), " About us"], href="/about", className="ml-2, navitem", n_clicks=0
                        ),
            width="auto"
        ),
        ],

        no_gutters=True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )]

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=LOGO, height="30px",
                            className="navitem")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/",
            style={"margin-right": "5rem"}
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            search_bar, id="navbar-collapse", navbar=True, is_open=False
        ),
    ],
    color="dark",
    dark=True,
)


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


#####################################################################################
correlation = '/assets/correlation-one2.png'
mintic = '/assets/mintic.png'


footer = html.Footer([html.Img(src=correlation, height="40px"), '       ', html.Img(src=mintic, height="40px")],
                     className="bg-dark text-inverse text-center py-4",
                     )


#####################################################################################
# LAYOUT
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[]), footer
])


#####################################################################################
# PAGES routes

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return main_menu.layout
    elif pathname == '/analysis/description':
        return description.layout
    elif pathname == '/analysis/reasons':
        return reasons.layout
    elif pathname == '/forecast/model_output':
        return model_output.layout
    elif pathname == '/about':
        return about.layout
    else:
        return '404'


server = app.server

# run the app
if __name__ == '__main__':
    app.run_server(debug=False)
    # app.run_server(host="0.0.0.0", port="80", debug=True)
