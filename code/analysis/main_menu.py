import os
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_html_components.Div import Div
import plotly.express as px
import plotly.graph_objs as go


# conditional graph
#####################################################################################
'''
@app.callback(Output('graph', 'style'), [Input('drop-down', 'value')])
def toggle_container(dropdown_value):
    if something
        return {'display': 'none'}
    else:
        return {'display': 'block'}
'''
#####################################################################################
feedback = '/assets/Anonymous_feedback_re_rc5v.svg'
analitic = '/assets/undraw_Charts_re_5qe9.svg'
forecast = '/assets/undraw_setup_analytics_8qkl.svg'
main = '/assets/customer-churn.png'


sections =  dbc.Card(
        dbc.CardBody([
          html.Div(dbc.Alert(
            [
                html.P("This project aims to avoid customer churn by analyzing previous data, understanding the reasons, and predicting future dropout cases. leading to a more efficient company that can focus it\'s resources on the right places."), 
            ],
            color="danger",
        ), style={ 'fontSize': 20, 'font-weight': 'bold'}) ,
          
          
            dbc.Row([
                dbc.Col([
                    html.Img(src=analitic, className="menu_img"), html.Div('Analitical description of the data',style={"font-weight":"bold"}), html.Div('Here you can find the graphs over time for all the relevant caracteristics of the businesses that withdraw and the overall businesses of positiva'), html.Br() ,dbc.Button( "Details ››", href='/analysis/description', className="ml-2 button", n_clicks=0
            ) , html.Br() 
                ], md=4),
                dbc.Col([
                    html.Img(src=feedback, className="menu_img"), html.Div('Feedback and comments of the clients',style={"font-weight":"bold"}), html.Div('This section includes the reason for withdrawal of some former clients, and some petitions, claims and complaints'), html.Br() ,dbc.Button(
                "Details ››", href='/analysis/reasons', className="ml-2 button", n_clicks=0
            ), html.Br() 
                ], md=4),
                dbc.Col([
                    html.Img(src=forecast,  className="menu_img"), html.Div('Forecast',style={"font-weight":"bold"}), html.Div('This section includes a forecast of the businesses that are more prone to leave the company'), html.Br() ,dbc.Button(
                "Details ››", href='/forecast/model_output' , className="ml-2 button", n_clicks=0
            ), html.Br() 
                ], md=4),
            ], align='center'), 
            html.Br(),   
            html.Div(html.Img(src=main, className="main_img")),
            html.Br(),  
            html.Br(),  
        ],style={"align-items":"center", 'background-color': '#ebebeb'}) )  # , color = 'dark'  




#####################################################################################
"""Layout"""
layout = html.Div(
    [sections]
)