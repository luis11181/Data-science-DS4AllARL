import os
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

from app import app
from data import cr, vx

#####################################################################################
"""TITULO"""
titulo = html.H2('WITHDRAWAL REASONS AND PQR DESCRIPTION')
#####################################################################################

##################################################
# Word Clouds

word_cloud = html.Div([
    html.Div(
        id='wordc',
        children=[
            html.H3('Customer\'s voice', style={'textAlign': 'center'}),
            dbc.Row([
                dbc.Col([
                    html.Div('Select n-gram:', style={'textAlign': 'right'}),
                    html.Div('Select year:', style={'textAlign': 'right'})
                ], md=0),
                dbc.Col([
                    dcc.Dropdown(
                        id='wordc_dd',
                        value='monogram',
                        options=[{'label': 'Monogram', 'value': 'monogram'},
                                 {'label': 'Bigram', 'value': 'bigram'},
                                 {'label': 'Trigram', 'value': 'trigram'}]),
                    # ], md=3),
                    dcc.Dropdown(
                        id='wordc_dd_date',
                        value='all',
                        options=[{'label': 'All', 'value': 'all'},
                                 {'label': '2019', 'value': '2019'},
                                 {'label': '2020', 'value': '2020'}])
                ], md=3),
            ]),
            dbc.CardImg(id='wordc_img', top=True,
                        style={"max-width": "40rem"}),
            # html.Img(id = 'wordc_img'),
        ])
], style={'width': '100%', 'padding': '0 20', 'textAlign': 'center'},  className="center")

# Callback para wordcloud


@app.callback(
    Output('wordc_img', 'src'),
    [Input('wordc_dd', 'value'),
     Input('wordc_dd_date', 'value')])
def update_word_cloud(value, year):

    if value == 'monogram':
        if year == 'all':
            return '/assets/word-clouds/monograms.png'
        else:
            return '/assets/word-clouds/monograms_{}.png'.format(year)

    elif value == 'bigram':
        if year == 'all':
            return '/assets/word-clouds/bigrams.png'
        else:
            return '/assets/word-clouds/bigrams_{}.png'.format(year)

    elif value == 'trigram':
        if year == 'all':
            return '/assets/word-clouds/trigrams.png'
        else:
            return '/assets/word-clouds/trigrams_{}.png'.format(year)

###############################################
# Motivos retiro


motivos_retiro = html.Div([
    html.Div(
        id='m_retiro',
        children=[
            html.H3('Withdrawal reasons', style={'textAlign': 'center'}),
            dbc.Row([
                dbc.Col([
                    dcc.Checklist(
                        id='m_retiro_cl',
                        options=[
                            {'label': 'Filter by year', 'value': 'True'},
                        ],
                        labelStyle={'display': 'inline-block'}
                    )
                ], md=3),

                dbc.Col(dcc.Graph(id='m_retiro_g', style={
                        "max-width": "40rem"}), md=12),

            ])
        ])
], style={'width': '100%', 'padding': '0 20', 'textAlign': 'center'},  className="center")

# Callback motivos retiro


@app.callback(
    Output('m_retiro_g', 'figure'),
    [Input('m_retiro_cl', 'value')]
)
def update_detalle_retiro(filter=False):
    if filter:
        return px.histogram(cr, y='detalle_causa', color='anio', barmode='group',
                            labels={
                                "detalle_causa": "Causa de retiro",
                                "anio": "Año",
                            })
    else:
        return px.histogram(cr, y='detalle_causa', labels={
            "detalle_causa": "Causa de retiro",
        })


#####################################################################################
# Encuestas

encuestas = html.Div([html.H3("Withdrawn clients' feedback",
                              style={'textAlign': 'center'}),
                      dash_table.DataTable(
    id='table',
    columns=[
        {'id': "numero", "name": "Company ID", 'editable': False},
        {'id': "fecha_radicacion", "name": "Issue date", 'editable': False},
        {'id': "causa_traslado", "name": "Cause (Short)", 'editable': False},
        {'id': "detalle_causa", "name": "Cause (Detail)", 'editable': False},
        {'id': "descripcion_traslado", "name": "Description", 'editable': False}
    ],
    data=vx.to_dict('records'),
    page_size=10,
    style_data={'whiteSpace': 'normal',
                'height': 'auto', 'textAlign': 'center'},
    style_header={'textAlign': 'Center',
                  'fontWeight': 'bold',
                  'border': '1px solid black',
                  'font_size': '15px'},
    style_data_conditional=[
        {'if': {'row_index': 'odd'},
         'backgroundColor': '#D8D8D8',
         }],
    style_cell={'border': '1px solid grey',
                'width': '180px',
                'minWidth': '200px',
                'maxWidth': '200px',
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'},
    style_table={'height': '1000px', 'overflowY': 'auto'},
    filter_action="native",
    sort_action='native',
    sort_mode="multi",
    fixed_rows={'headers': True})],
    style={'margin-right': '15px',
           "margin-left": "15px", 'vertical-align': 'top'}

)

#####################################################################################
# Layout


layout = html.Div(
    [titulo,
        html.Div([
            html.Br(),
            dbc.Alert(
                [
                    html.P("The following section shows the withdrawal reasons submmited by the companies that did leave positiva, the most representing words between all the reasons can be selected by the number of words, and by year; giving a great and short description of the most important reasons for withdrawal shared by the clients"),
                ],
                color="info",
            ),
            dbc.Row([
                dbc.Col([
                    word_cloud
                ], md=6),
                dbc.Col([
                    motivos_retiro
                ], md=6),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    encuestas
                ], md=12)
            ]),
        ], style={'width': '100%', 'padding': '0 20', "align-items": "center", 'border-style': 'none'}, className="center")
     ], style={'width': '100%', 'padding': '0 20', "align-items": "center", 'border-style': 'none'})
