import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import DataTable, FormatTemplate

from app import app
from .model_eval import model_predict_proba

#####################################################################################
"""TITULO"""
titulo = html.H2('Withdrawal forecast')
#####################################################################################
# Model evaluation
model_output = model_predict_proba()

#####################################################################################
# Heatmap formatter
# taken from https://dash.plotly.com/datatable/conditional-formatting

# El número de colores que se puede poner es entre 3 y 11 (inclusive)


def discrete_background_color_bins(df, n_bins=10, columns='all', probability=True):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes(
                'number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    if probability:
        df_max = 1
        df_min = 0
    else:
        df_max = df_numeric_columns.max().max()
        df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(
            n_bins)]['div']['RdYlGn'][-i]
        color = 'white' if (i < len(bounds) * (1/4)) or (i >
                                                         len(bounds) * (3/4)) else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (
                            i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))


(styles, legend) = discrete_background_color_bins(
    model_output, columns=['prob'])


#####################################################################################
# Table layout
forecast = html.Div([html.H3("Withdrawal probability prediction for current month",
                             style={'textAlign': 'center'}),
                     html.Div(legend, style={'float': 'right'}),
                     DataTable(
    id='model_output_table',
    columns=[
        {'id': "numero", "name": "Company ID", 'editable': False},
        {'id': "seccion", "name": "Economic sector", 'editable': False},
        {'id': "departamento", "name": "Province", 'editable': False},
        {'id': "municipio", "name": "Municipality", 'editable': False},
        {'id': "segmento", "name": "Cluster", 'editable': False},
        {'id': "tamano_emp", "name": "Company size", 'editable': False},
        {'id': "prob", "name": "Probability", 'editable': False,
         'type': 'numeric', 'format': FormatTemplate.percentage(2)}
    ],
    data=model_output.to_dict('records'),
    page_size=15,
    style_data={'whiteSpace': 'normal',
                'height': 'auto', 'textAlign': 'center'},
    style_header={'textAlign': 'Center',
                  'fontWeight': 'bold',
                  'border': '1px solid black',
                  'font_size': '15px'},
    style_data_conditional=styles,
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

"""Layout"""

layout = html.Div(
    [titulo,
     dbc.Alert(
         [
             html.P("The following section shows the model forecast, of the companies that are more likely to withdraw from the company, this model don't takes unipersonal and microempresas into account, due to the uncertain behavior of this really small companies."),
         ],
         color="info",
     ),
     forecast]
)
