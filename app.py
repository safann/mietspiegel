#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import plotly.express as px
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


app = dash.Dash(__name__)

df_beschr = pd.read_csv("beschreibung.csv")
df_bez = pd.read_csv("bezdata.csv")
df_mietsp = pd.read_csv("mietspiegel.csv")
with open('muenchen.geo.json') as f:
    geojson = json.load(f)


df_bez = df_bez.rename(columns={"bez": "District"})
df_mietsp = df_mietsp.rename(columns={"bez": "District"})

df_merged = pd.merge(df_beschr, df_bez, on='District')
df_merged = df_merged.drop(['bez_name'], axis=1)
df_merged = pd.merge(df_merged, df_mietsp, on='District')


single_year = df_merged.groupby((df_merged["bjahr"]//10)*10).get_group(1990)

# creation of app layout
app.layout = html.Div([
    html.H1("Mietspiegel in München", style={'text-align': 'center'}),

    dcc.Dropdown(
        id="slct_year", clearable=False,
        value=1910,
        options=[{"label": str(year), "value": year}
                 for year in range(1910, 2000, 10)]
    ),
    html.Div(id='output_container'),
    html.Br(),
    html.Div([
        dcc.Graph(id='mietspiegel', figure={}),
        dcc.Graph(id='mietspiegel2', figure={})

    ], style={
        'display': 'flex',
        'flex-wrap': 'wrap'
    })
])

# Define callback to update graph
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='mietspiegel', component_property='figure'),
     Output(component_id='mietspiegel2', component_property='figure'),
     ],
    [Input(component_id="slct_year", component_property='value')]
)
def update_figure(option_slctd):
    container = ["The year chosen by user is: {}".format(option_slctd)]

    single_year = df_merged.groupby(
        (df_merged["bjahr"]//10)*10).get_group(option_slctd)

    # Map graph

    fig = px.choropleth(
        single_year,
        locations='District',
        geojson=geojson,
        featureidkey="properties.id",
        hover_data=['District name', 'Fläche (ha)', 'Einw./ha'],
        color='Einw./ha',
        labels={'Einw./ha': 'Districts density'},
    )
    fig2 = px.choropleth(
        single_year,
        locations='District',
        geojson=geojson,
        featureidkey="properties.id",
        hover_data=['District name', 'mieteqm'],
        color='mieteqm',
        labels={'mieteqm': 'Rent per sqm'},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig2.update_geos(fitbounds="locations", visible=False)
    return container, fig, fig2


app.run_server()
