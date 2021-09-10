import json
from urllib.request import urlopen
import os
import dash
import pandas as pd
import numpy as np
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
from itertools import cycle

from app import app

from data import df

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


# grafica1
# Generar lista de opciones para el Dropdown
#ddw_opts = [{'label':column, 'value':column} for column in df.columns]
# TODO: Mostrar solamente columnas numéricas
# TODO: Hacer un diccionario con el nombre de cada columna


#####################################################
# grafica , la grafca grande segunda


categorias_activas = [{'label': 'all', 'value': 'retiro'}, {
    'label': 'Company size', 'value': 'tamano_emp'}, {'label': 'Segment', 'value': 'segmento'}]

grafica_empresas = html.Div([
    html.Div(
        id='basico1',
        children=[
            html.H3('Companies over time'),
            dbc.Row([dbc.Col([
                    html.Div()
                    ], md=6),
                dbc.Col([
                    html.Div('Fragment active companyes by category:',
                             style={'textAlign': 'right'})
                ], md=3),
                dbc.Col([
                    dcc.Dropdown(
                        id='caracteristica1',
                        value='retiro',
                        options=categorias_activas)
                ], md=3),
            ], align='center'),
            dbc.Row([
                dbc.Col([dcc.Graph(id='linegraphretiros2')

                         ], md=6),
                dbc.Col([dcc.Graph(id='linegraphactivas')

                         ], md=6),
            ], align='center'),

        ])
], style={'width': '100%', 'padding': '0 20'},  className="center")

# callback para primera grafica, aun experimental
# Callbacks para gráficos interactivos


@app.callback(
    [Output('linegraphactivas', 'figure'),
     Output('linegraphretiros2', 'figure')],
    [Input('caracteristica1', 'value')])
def update_activas(caracteristica1):
    if caracteristica1 is None:
        caracteristica1 = 'retiro'

    activas = df[df['retiro'] == 0].groupby(
        [caracteristica1, 'corte']).sum().reset_index()
    figactivas = px.line(activas, x='corte',
                         y='ocurrencias', color=caracteristica1,
                         template="simple_white")

    retiradas = df[df['retiro'] != 0].groupby(
        ['retiro', 'corte']).sum().reset_index()
    figretiros = px.line(retiradas, x='corte', y='ocurrencias', color='retiro',
                         template="simple_white")

    figactivas.update_layout(
        title="Active companies",
        xaxis_title="Time",
        yaxis_title="# of events by month")

    figretiros.update_layout(
        title="Withdrawed and inactive companies",
        xaxis_title="Time",
        yaxis_title="# of events by month",
        legend_title="State")

    # updates the legend
    names = cycle(['Official', 'Not official', 'Inactive'])
    figretiros.for_each_trace(lambda t:  t.update(name=next(names)))

    return figactivas, figretiros


''' cambiar el color del fondo de las graficas

    .update_layout( {
            #'plot_bgcolor': 'rgba(200, 200, 200, 0.8)',
            'paper_bgcolor': 'rgba(255, 255, 255, 0.3)',

            'font': {
                #'color': '#531900'
                # 'color': '#FFFFFF'
                'color': '#000000'
            }
        })
'''


#####################################################
# grafica de retiros formales e informale a lo largo del tiempo

grafica_retiros = html.Div([
    html.Div(
        id='basico2',
        children=[
            html.H3('Withdrawals by category over time'),
            html.Br(),
            dbc.Row([dbc.Col([
                    html.Div('Y axis selector:', style={'textAlign': 'right'})
                    ], md=2, align="right"),
                dbc.Col([
                    dcc.Dropdown(
                        id='selector_y_retiro',
                        value='ocurrencias',
                        options=[{'label': '# of events by month', 'value': 'ocurrencias'}, {'label': 'avg(prima)', 'value': 'avg_prima'}, {'label': 'avg(recaudo)', 'value': 'avg_recaudo'}])
                ], md=2),
                dbc.Col([
                    html.Div('Status:', style={'textAlign': 'right'})
                ], md=2),
                dbc.Col([
                    dcc.Dropdown(
                        id='tipo_retiro',
                        value=4,
                        options=[{'label': 'retiros totales', 'value': 4}, {'label': 'retiro formal', 'value': 1}, {'label': 'retiro informal', 'value': 2}, {'label': 'inactive', 'value': 3}])
                ], md=2),
                dbc.Col([
                    html.Div('Grouping category:', style={
                             'textAlign': 'right'})
                ], md=2),
                dbc.Col([
                    dcc.Dropdown(
                        id='caracteristica2',
                        value='tamano_emp',
                        options=[{'label': 'economic sector', 'value': 'descripcion_seccion'}, {'label': 'companies size', 'value': 'tamano_emp'}, {'label': 'department', 'value': 'departamento'}, {'label': 'segment', 'value': 'segmento'}])
                ], md=2),
            ]),
            dcc.Graph(id='linegraph_retiros2')]),
    dcc.Slider(
        id='year_slider',
        min=2016,  # pd.to_datetime(df['corte']).min(),
        max=2022,
        value=2022,
        marks={'2016': '2016', '2017': '2017', '2018': '2018', '2019': '2019', '2020': '2020',
               '2022': 'all'},  # str(year): str(year) for year in pd.to_datetime(df['corte']).unique()
        step=None
    )
], style={'width': '100%', 'padding': '0 20'},  className="center")

# callback para primera grafica, aun experimental
# Callbacks para gráficos interactivos


@app.callback(
    Output('linegraph_retiros2', 'figure'),
    [Input('caracteristica2', 'value'),
     Input('selector_y_retiro', 'value'),
     Input('tipo_retiro', 'value'),
     Input('year_slider', 'value')])
def update_inactivas(caracteristica2, selector_y_retiro, tipo_retiro, year_slider):

    if caracteristica2 is None:
        caracteristica2 = 'tamano_emp'

    if tipo_retiro is None:
        tipo_retiro = 2

    if selector_y_retiro is None:
        selector_y_retiro = 'ocurrencias'

    if year_slider == 2022:
        if tipo_retiro == 4:
            retiradas = df[(df['retiro'] == 2) | (df['retiro'] == 1)].groupby(
                [caracteristica2, 'corte']).sum().reset_index()
        else:
            retiradas = df[(df['retiro'] == tipo_retiro)].groupby(
                [caracteristica2, 'corte']).sum().reset_index()
    else:
        if tipo_retiro == 4:
            retiradas = df[((df['retiro'] == 2) | (df['retiro'] == 1)) & (
                df['year'] == year_slider)].groupby([caracteristica2, 'corte']).sum().reset_index()
        else:
            retiradas = df[(df['retiro'] == tipo_retiro) & (df['year'] == year_slider)].groupby(
                [caracteristica2, 'corte']).sum().reset_index()

    figretiros2 = px.line(retiradas, x='corte',
                          y=selector_y_retiro, color=caracteristica2,
                          template="simple_white")

    figretiros2.update_layout(
        title="Withdrawed and inactive companies by category",
        xaxis_title="Time",
        yaxis_title=selector_y_retiro,
        legend_title=caracteristica2)

    # avoid legend when showing large description legend
    if caracteristica2 == 'descripcion_seccion':
        figretiros2.update_layout(showlegend=False)

    return figretiros2


#####################################################
# grafica de retiros normalizados sobre las empresas activas

grafica_retiros_normalizados = html.Div([
    html.Div(
        id='basico2',
        children=[
            html.H3('Normalized withdrawals by category over time',
                    style={'textAlign': 'center'}),
            dbc.Row([
                dbc.Col([
                    html.Div('Grouping category:', style={
                             'textAlign': 'right'})
                ], md=0),
                dbc.Col([
                    dcc.Dropdown(
                        id='caracteristica3',
                        value='all',
                        options=[{'label': 'All', 'value': 'all'}, {'label': 'economic sector', 'value': 'descripcion_seccion'}, {'label': 'companies size', 'value': 'tamano_emp'}, {'label': 'department', 'value': 'departamento'}])
                ], md=2),
            ]),
            dcc.Graph(id='linegraph_retiros_normalizados')])
], style={'width': '100%', 'padding': '0 20', 'textAlign': 'right'},  className="center")

#
# Callbacks para gráficos interactivos


@app.callback(
    Output('linegraph_retiros_normalizados', 'figure'),
    [Input('caracteristica3', 'value')])
def update_inactivas_norm(caracteristica3):

    if caracteristica3 is None:
        caracteristica3 = 'all'

    if caracteristica3 == 'all':

        activas = df[df['retiro'] == 0].groupby(['corte']).sum().reset_index()
        retiradas = df[((df['retiro'] == 2) | (df['retiro'] == 1))].groupby(
            ['corte']).sum().reset_index()  # or df['retiro'] == 1

        retiradas_normalizadas = pd.merge(retiradas, activas, left_on=['corte'], right_on=[
                                          'corte'], suffixes=('_retiradas', '_total'))

        retiradas_normalizadas['porcentaje_retiros'] = retiradas_normalizadas['ocurrencias_retiradas'] / \
            retiradas_normalizadas['ocurrencias_total']*100
        figretirosnormalizados = px.line(
            retiradas_normalizadas, x='corte', y='porcentaje_retiros',
            template="simple_white")

    else:

        activas = df[df['retiro'] == 0].groupby(
            [caracteristica3, 'corte']).sum().reset_index()
        retiradas = df[df['retiro'] == 2].groupby(
            [caracteristica3, 'corte']).sum().reset_index()  # or df['retiro'] == 1

        retiradas_normalizadas = pd.merge(retiradas, activas, left_on=[caracteristica3, 'corte'], right_on=[
                                          caracteristica3, 'corte'], suffixes=('_retiradas', '_total'))

        retiradas_normalizadas['porcentaje_retiros'] = retiradas_normalizadas['ocurrencias_retiradas'] / \
            retiradas_normalizadas['ocurrencias_total']*100
        figretirosnormalizados = px.line(
            retiradas_normalizadas, x='corte', y='porcentaje_retiros', color=caracteristica3,
            template="simple_white")

    figretirosnormalizados.update_layout(
        title="(Withdrawed companies/active companies) by category",
        xaxis_title="Time",
        yaxis_title='Percentage of events %',
        legend_title=caracteristica3)

    # avoid legend when showing large description legend
    if caracteristica3 == 'descripcion_seccion':
        figretirosnormalizados.update_layout(showlegend=False)

    return figretirosnormalizados


#####################################################################################
# MAPAS, codigo para los 3 mapas
# A) Cargando los datos espaciales

geojson = px.data.election_geojson()
with urlopen('https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json') as response:
    geojson = json.load(response)


#####################################################################################
# mapa 1 activas


categorias_mapas = [{'label': 'none', 'value': 'none'}, {'label': 'economic sector',
                                                         'value': 'descripcion_seccion'}, {'label': 'Segment', 'value': 'segmento'}]

mapa_empresas = html.Div([
    html.Div(
        id='mapa1',
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div('Filter by:', style={
                                     'textAlign': 'right'}),

                            dcc.Dropdown(
                                id='map_filter',
                                value='none',
                                options=categorias_mapas)
                        ], md=12)]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Search parameter of the filter:',
                                     style={'textAlign': 'right'}),

                            dcc.Dropdown(
                                id='map_data',)
                        ], md=12),
                    ])
                ], md=3),
                dbc.Col([dcc.Graph(id='map_activas')

                         ], md=9),
            ], align='center'),

            dcc.Slider(
                id='map_year_slider',
                min=20163,  # pd.to_datetime(df['corte']).min(),
                max=20211,
                value=20213,
                marks={'20166': '20166', '201612': '201612', '20171': '20171', '20176': '20176', '20181': '20181', '20186': '20186', '20191': '20191',
                       '20196': '20196', '20201': '20201', '20206': '20206', '20211': '20211'},  # str(year): str(year) for year in df['yearmonth'].unique()
                step=None
            )

        ])
], style={'width': '100%', 'padding': '0 20'},  className="center")

# callback para primera grafica, aun experimental
# Callbacks para gráficos interactivos


@app.callback(
    Output('map_data', 'options'),
    [Input('map_filter', 'value')]
)
def update_map_activas_dropdown(map_filter):

    if map_filter == "none":
        List = ''
    else:
        List = pd.Series(df[map_filter].unique())

    return [{'label': i, 'value': i} for i in List]


@app.callback(
    Output('map_activas', 'figure'),
    [Input('map_filter', 'value'),
     Input('map_data', 'value'),
     Input('map_year_slider', 'value')])
def update_map_activas(map_filter, map_data, map_year_slider):

    if map_filter == "none":

        df_mapa = df[(df['retiro'] == 0) & (df.yearmonth == map_year_slider)].groupby(
            ['divipola']).sum().reset_index()

        Min_Value = df_mapa['ocurrencias'].min()
        Max_Value = df_mapa['ocurrencias'].max()
    else:

        df_mapa = df[(df[map_filter] == map_data) & (df['retiro'] == 0) & (
            df.yearmonth == map_year_slider)].groupby([map_filter, 'divipola']).sum().reset_index()

        Min_Value = df_mapa['ocurrencias'].min()
        Max_Value = df_mapa['ocurrencias'].max()

    mapa1 = px.choropleth(
        df_mapa,
        geojson=geojson,
        color="ocurrencias",
        locations="divipola",
        featureidkey="properties.DPTO",
        projection="mercator",
        range_color=[Min_Value, Max_Value],
        template="simple_white")

    mapa1.update_geos(fitbounds="locations", visible=True, showcoastlines=True,
                      showland=True, bgcolor="#D4DADC", landcolor="#FAFAF8")

    mapa1.update_geos(fitbounds="locations", visible=True, showcoastlines=True, showland=True,
                      bgcolor="#D4DADC", landcolor="#FAFAF8", showcountries=True, countrycolor="#bdbdbd")

    # "t":0   , showlegend=True
    mapa1.update_layout(margin={"r": 0, "l": 0, "b": 0})

    mapa1.update_layout(
        title_text='Active companies by year, by category')

    return mapa1

###################################################################################
#####################################################################################
# mapa 2 desafiliadas


mapa_retiros = html.Div([
    html.Div(
        id='mapa1',
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div('Filter by:', style={
                                     'textAlign': 'right'}),
                            dcc.Dropdown(
                                id='map_filter2',
                                value='none',
                                options=categorias_mapas)
                        ], md=12)]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Search parameter of the filter:',
                                     style={'textAlign': 'right'}),

                            dcc.Dropdown(
                                id='map_data2',)
                        ], md=12),
                    ])
                ], md=3),
                dbc.Col([dcc.Graph(id='map_retiros')

                         ], md=9),
            ], align='center'),

            dcc.Slider(
                id='map_year_slider2',
                min=20163,  # pd.to_datetime(df['corte']).min(),
                max=20211,
                value=20206,
                marks={'20166': '20166', '201612': '201612', '20171': '20171', '20176': '20176', '20181': '20181', '20186': '20186', '20191': '20191',
                       '20196': '20196', '20201': '20201', '20206': '20206', '20211': '20211'},  # str(year): str(year) for year in df['yearmonth'].unique()
                step=None
            )

        ])
], style={'width': '100%', 'padding': '0 20'},  className="center")

# callback para primera grafica, aun experimental
# Callbacks para gráficos interactivos


@app.callback(
    Output('map_data2', 'options'),
    [Input('map_filter2', 'value')]
)
def update_map_activas_dropdown(map_filter):

    if map_filter == "none":
        List = ''
    else:
        List = pd.Series(df[map_filter].unique())

    return [{'label': i, 'value': i} for i in List]


@app.callback(
    Output('map_retiros', 'figure'),
    [Input('map_filter2', 'value'),
     Input('map_data2', 'value'),
     Input('map_year_slider2', 'value')])
def update_map_activas(map_filter, map_data, map_year_slider):

    if map_filter == "none":

        df_mapa = df[((df['retiro'] == 2) | (df['retiro'] == 1)) & (
            df.yearmonth == map_year_slider)].groupby(['divipola']).sum().reset_index()

        Min_Value = df_mapa['ocurrencias'].min()
        Max_Value = df_mapa['ocurrencias'].max()
    else:

        df_mapa = df[(df[map_filter] == map_data) & ((df['retiro'] == 2) | (df['retiro'] == 1)) & (
            df.yearmonth == map_year_slider)].groupby(['divipola']).sum().reset_index()

        Min_Value = df_mapa['ocurrencias'].min()
        Max_Value = df_mapa['ocurrencias'].max()

    mapa2 = px.choropleth(
        df_mapa,
        geojson=geojson,
        color="ocurrencias",
        locations="divipola",
        featureidkey="properties.DPTO",
        projection="mercator",
        range_color=[Min_Value, Max_Value])

    mapa2.update_geos(fitbounds="locations", visible=True, showcoastlines=True,
                      showland=True, bgcolor="#D4DADC", landcolor="#FAFAF8")

    mapa2.update_geos(fitbounds="locations", visible=True, showcoastlines=True, showland=True,
                      bgcolor="#D4DADC", landcolor="#FAFAF8", showcountries=True, countrycolor="#bdbdbd")

    # "t":0   , showlegend=True
    mapa2.update_layout(margin={"r": 0, "l": 0, "b": 0})

    mapa2.update_layout(
        title_text='Withdrawed companies by year, by category')

    return mapa2


###################################################################################
#####################################################################################
# mapa DATOS NORMALIZADOS
mapa_retiros_normalizados = html.Div([
    html.Div(
        id='mapa1',
        children=[
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div('Filter by:', style={
                                     'textAlign': 'right'}),
                            dcc.Dropdown(
                                id='map_filter3',
                                value='none',
                                options=categorias_mapas)
                        ], md=12)]),
                    dbc.Row([
                        dbc.Col([
                            html.Div('Search parameter of the filter:',
                                     style={'textAlign': 'right'}),

                            dcc.Dropdown(
                                id='map_data3',)
                        ], md=12),
                    ])
                ], md=3),
                dbc.Col([dcc.Graph(id='map_retiros_normalizados')

                         ], md=9),
            ], align='center'),

            dcc.Slider(
                id='map_year_slider3',
                min=20163,  # pd.to_datetime(df['corte']).min(),
                max=20211,
                value=20206,
                marks={'20166': '20166', '201612': '201612', '20171': '20171', '20176': '20176', '20181': '20181', '20186': '20186', '20191': '20191',
                       '20196': '20196', '20201': '20201', '20206': '20206', '20211': '20211'},  # str(year): str(year) for year in df['yearmonth'].unique()
                step=None
            )

        ])
], style={'width': '100%', 'padding': '0 20'},  className="center")

# callback para primera grafica, aun experimental
# Callbacks para gráficos interactivos


@app.callback(
    Output('map_data3', 'options'),
    [Input('map_filter3', 'value')]
)
def update_map_activas_dropdown(map_filter):

    if map_filter == "none":
        List = ''
    else:
        List = pd.Series(df[map_filter].unique())

    return [{'label': i, 'value': i} for i in List]


@app.callback(
    Output('map_retiros_normalizados', 'figure'),
    [Input('map_filter3', 'value'),
     Input('map_data3', 'value'),
     Input('map_year_slider3', 'value')])
def update_map_activas(map_filter3, map_data3, map_year_slider3):

    if map_filter3 == "none":

        activas = df[(df['retiro'] == 0) & (df.yearmonth == map_year_slider3)].groupby(
            ['divipola']).sum().reset_index()

        retiradas = df[((df['retiro'] == 2) | (df['retiro'] == 1)) & (
            df.yearmonth == map_year_slider3)].groupby(['divipola']).sum().reset_index()

        retiradas_normalizadas = pd.merge(retiradas, activas, left_on=['divipola'], right_on=[
                                          'divipola'], suffixes=('_retiradas', '_total'))

        retiradas_normalizadas['porcentaje_retiros%'] = retiradas_normalizadas['ocurrencias_retiradas'] / \
            retiradas_normalizadas['ocurrencias_total']*100

        Min_Value = retiradas_normalizadas['porcentaje_retiros%'].min()
        Max_Value = retiradas_normalizadas['porcentaje_retiros%'].max()
    else:

        retiradas = df[(df[map_filter3] == map_data3) & ((df['retiro'] == 2) | (df['retiro'] == 1)) & (
            df.yearmonth == map_year_slider3)].groupby(['divipola']).sum().reset_index()

        activas = df[(df[map_filter3] == map_data3) & (df['retiro'] == 0) & (
            df.yearmonth == map_year_slider3)].groupby(['divipola']).sum().reset_index()

        retiradas_normalizadas = pd.merge(retiradas, activas, left_on=['divipola'], right_on=[
                                          'divipola'], suffixes=('_retiradas', '_total'))

        retiradas_normalizadas['porcentaje_retiros%'] = retiradas_normalizadas['ocurrencias_retiradas'] / \
            retiradas_normalizadas['ocurrencias_total']*100

        Min_Value = retiradas_normalizadas['porcentaje_retiros%'].min()
        Max_Value = retiradas_normalizadas['porcentaje_retiros%'].max()

    mapa3 = px.choropleth(
        retiradas_normalizadas,
        geojson=geojson,
        color="porcentaje_retiros%",
        locations="divipola",
        featureidkey="properties.DPTO",
        projection="mercator",
        range_color=[Min_Value, Max_Value])

    mapa3.update_geos(fitbounds="locations", visible=True, showcoastlines=True,
                      showland=True, bgcolor="#D4DADC", landcolor="#FAFAF8")

    mapa3.update_geos(fitbounds="locations", visible=True, showcoastlines=True, showland=True,
                      bgcolor="#D4DADC", landcolor="#FAFAF8", showcountries=True, countrycolor="#bdbdbd")

    # "t":0   , showlegend=True
    mapa3.update_layout(margin={"r": 0, "l": 0, "b": 0})

    mapa3.update_layout(
        title_text='(Withdrawed companies/active companies) by year, by category')

    return mapa3


#####################################################################################
"""TITULO"""
titulo = html.H2('DATA EXPLORATION ')

#####################################################################################

#####################################################################################


"""Layout"""
layout = html.Div(
    [titulo, html.Div(
        dbc.CardBody([
            html.Br(),
            dbc.Row([
                dbc.Alert(
                    [
                        html.P("The following section shows the behavior of withdrawed and active companies that were enrolled in Positiva over time, plotting all companies, except unipersonal, due to the uncertain behavior of these really small companies."),
                    ],
                    color="info",
                ),
                dbc.Alert(
                    [
                        html.P(
                            "According to each company's payment records and status information, they were grouped in one of the following categories for each month:"),
                        html.Hr(),
                        html.P(
                            "Active: A company that is actively paying it's monthly fee and has no defaults, or no records for more than six months"),
                        html.P(
                            "Official retired: A company that presented an official letter to Positiva informing they would leave the company on a specific month"),
                        html.P("Informal/ not offically retired: A company that presented defaults or no records for more than six months in a row, giving then the status of retired, this status is given only in the last month that they made the last payment fee to Positiva"),
                        html.P("Inactive: A company that presented a retirement but did comeback in the future, this companies will sustain an inactive status from the month they have the retirement status until the present a new positive payment fee again"),
                        html.P(
                            "Deleted: If a company retires and does not comeback to the company again is deleted and not taken into account for future record or plots")
                    ],
                    color="secondary",
                ),
                dbc.Col([
                    grafica_empresas
                ], md=12),
            ], align='center'),
        ], style={"align-items": "center"})),

        html.Div(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    mapa_empresas
                ], md=12),
            ], align='center'),
            html.Br(),
        ], style={"align-items": "center", 'border-style': 'none'}, className="center")),

        html.Div(
        dbc.CardBody([
            html.Br(),
            dbc.Row([
                dbc.Col([
                    grafica_retiros
                ], md=12),
            ], align='center'),
        ], style={"align-items": "center"})),

        html.Div(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                        mapa_retiros
                        ], md=12),
            ], align='center'),
            html.Br(),
        ], style={"align-items": "center", 'border-style': 'none'}, className="center")),

        html.Div(
        dbc.CardBody([
            html.Br(),
            dbc.Row([
                dbc.Col([grafica_retiros_normalizados
                         ], md=12),
            ], align='center'),
        ], style={"align-items": "center"})),

        html.Div(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                        mapa_retiros_normalizados
                        ], md=12),
            ], align='center'),
            html.Br(),
        ], style={"align-items": "center", 'border-style': 'none'}, className="center")),

     ]
)
