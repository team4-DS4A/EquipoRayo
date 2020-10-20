import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

from datetime import datetime as dt
import json
import numpy as np
import pandas as pd
import os

from app import app


discharges = pd.read_csv('./data/discharges.csv', header=0, delimiter=',', index_col=0,
                         names=['date', 'longitude', 'latitude', 'polarity', 'magnitude', 'current'], parse_dates=['date'])
outages = pd.read_csv('./data/outages.csv', header=0, delimiter=',', index_col=0,
                     names=['date', 'year', 'time', 'cause', 'outages_number', 'r_inf', 'r_sup'], parse_dates=['date'])
towers = pd.read_csv('./data/towers.csv', header=0,
                     delimiter=',', names=['longitude', 'latitude'])

discharges_all_outages = pd.DataFrame(columns=discharges.columns)

def Discharges_before_outage_by_time(outage_date, time_range, min_before=5):
    datetime_f = outage_date - timedelta(minutes=min_before)
    datetime_i = datetime_f - timedelta(minutes=time_range)
    discharges_copy = discharges.copy()
    discharges_before_outage_by_time = discharges_copy[(discharges['date'] > datetime_i) &
                        (discharges_copy['date'] < datetime_f)].reset_index()
    return discharges_before_outage_by_time


discharges_outage_1 = Discharges_before_outage_by_time(outages['date'][0], 20)

map_fig = go.Figure()
map_fig.add_trace(go.Scattermapbox(
    lat=discharges_outage_1.latitude,
    lon=discharges_outage_1.longitude,
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=7,
        color='blue',
        opacity=0.7
    ),
))
map_fig.add_trace(go.Scattermapbox(
    lat=towers.latitude,
    lon=towers.longitude,
    mode='markers+lines',
    marker=go.scattermapbox.Marker(
        size=7,
        color='black',
        opacity=0.7
    ),
))
map_fig.update_layout(
    title='Electric discharges of the last 20 minutes',
    autosize=True,
    # hovermode='closest',
    showlegend=True,
    # mapbox_style="open-street-map",
    height=700,
    mapbox=dict(
        style='open-street-map',
    #    accesstoken=mapbox_access_token,
    #    bearing=0,
        center=dict(
            lat=6.73,
            lon=-73.9
        ),
    #    pitch=0,
        zoom=8
    #    style='light'
))
#################################################################################
# Here the layout for the plots to use.
#################################################################################
stats = html.Div(
    [
        html.Div(
            [
                dcc.Graph(figure=map_fig, id="fig-id",style = {'width': '100%', 'height':'650%'})
             ]
            ),
        html.Div([html.Label(children='From 2007 to 2017', id='time-range-label'),dcc.RangeSlider(
                id='year_slider',
                min=0,
                max=30,
                step=1,
                marks={i:f'{i}' for i in range(30)},
                value=[5, 10])]),
    ],
    className="ds4a-body",
)

# the value of RangeSlider causes Label to update
@app.callback(
    output=Output(component_id = 'time-range-label',component_property= 'children'),
    inputs=[Input(component_id = 'year_slider', component_property='value')]
    )
def _update_time_range_label(year_range):
    return 'From {} to {}'.format(year_range[0], year_range[1])

# the value of RangeSlider causes Graph to update
@app.callback(
    output=Output('fig-id', 'figure'),
    inputs=[Input(component_id = 'year_slider', component_property='value'),
            Input('outage_dropdown','value')
            ],
    )
def _update_graph(year_range, outage_indicator):
    print(year_range)
    print(outages.loc[outage_indicator,'date'])
    outage_date = outages.loc[outage_indicator,'date']
    min_start = year_range[0]
    min_end = year_range[1]
    discharges_outage_1 = Discharges_before_outage_by_time(outage_date, min_end,min_start)
    map_fig = go.Figure()
    map_fig.add_trace(go.Scattermapbox(
        lat=discharges_outage_1.latitude,
        lon=discharges_outage_1.longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=7,
            color=discharges_outage_1.magnitude,
            opacity=0.7,
            showscale=True,
        ),
    ))
    map_fig.add_trace(go.Scattermapbox(
        lat=towers.latitude,
        lon=towers.longitude,
        mode='markers+lines',
        marker=go.scattermapbox.Marker(
            size=7,
            color='black',
            opacity=0.7
        ),
    ))
    map_fig.update_layout(
        title='Electric discharges of the last 20 minutes',
        autosize=True,
        height=700,
        showlegend=True,
        # hovermode='closest',
        # mapbox_style="open-street-map",
        mapbox=dict(
            style='open-street-map',
        #    accesstoken=mapbox_access_token,
        #    bearing=0,
            center=dict(
                lat=6.73,
                lon=-73.9
            ),
            zoom=8
    ))
    map_fig['layout']['uirevision'] = 'no reset of zoom'
    return map_fig