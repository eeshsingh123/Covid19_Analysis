import time
import random
from collections import Counter

import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event
import plotly
import plotly.graph_objs as go

from misc.sql_operations import SqlHelper
from config import APP_COLORS, BASE_PATH, TABLE_NAME
from tools.generate_table import generate_table

app = dash.Dash(__name__)

sql_helper = SqlHelper()
covid_data = pd.read_csv(f"{BASE_PATH}\\twitter_db\\kaggle_data\\covid_19_data.csv")
covid_data["ObservationDate"] = pd.to_datetime(covid_data["ObservationDate"])
covid_data["Last Update"] = pd.to_datetime(covid_data["Last Update"])

most_common_countries = [k for k, _ in Counter(covid_data["Country/Region"]).most_common(150)]

app.layout = html.Div([
    # style={"background-color": APP_COLORS["background"]},
    html.Div([
        html.Div([
            html.Label("County specific data"),
            dcc.Dropdown(
                id="dropdown-countries",
                options=[{"label": i, "value": i} for i in most_common_countries],
                value=['Mainland China'],
                multi=True
            ),
            dcc.RadioItems(
                id="radio-y-type",
                options=[{"label": i, "value": i} for i in ["Confirmed", "Deaths", "Recovered"]],
                value="Confirmed",
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id="corona-worldwide")
        ], className="six columns"),

        html.Div([
            html.Label("All data for a Country"),
            dcc.Dropdown(
                id="dropdown-1-country",
                options=[{"label": i, "value": i} for i in most_common_countries],
                value="Mainland China",
                multi=False
            ),
            dcc.Graph(id="all-3-graph")
        ], className="six columns"),
    ], className="row"),

    html.Div(className='row', children=[html.Div(id="recent-tweets-table", className='col s12 m6 l6')],
             style={'width': '50%'}),

    dcc.Interval(
        id='recent-table-update',
        interval=10 * 1000,
    )]
)


@app.callback(Output(component_id='corona-worldwide', component_property='figure'),
              [Input(component_id='dropdown-countries', component_property='value'),
               Input(component_id='radio-y-type', component_property='value')])
def display_country_specific_data(country, display_type):
    graph = []
    for cname in country:
        agg_df = covid_data[covid_data["Country/Region"] == cname].groupby("ObservationDate").agg(
            {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}).reset_index()
        graph.append(
            go.Scatter(
                x=agg_df["ObservationDate"],
                y=agg_df[display_type],
                mode="lines",
                opacity=0.5,
                name=cname
            )
        )
    graphs = [graph]
    data = [val for sublist in graphs for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1',
                            '#FF7400', '#FFF400', '#FF0056'],
                  height=600,
                  title=f"Covid-19 {display_type} cases",
                  xaxis={"title": "ObservationDate"},
                  yaxis={"title": display_type}
              )}
    return figure


@app.callback(Output(component_id='all-3-graph', component_property='figure'),
              [Input(component_id='dropdown-1-country', component_property='value')])
def display_all_data(country):
    agg_df = covid_data[covid_data["Country/Region"] == country].groupby("ObservationDate").agg(
        {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}).reset_index()
    figure = {
        "data": [
            {"x": agg_df["ObservationDate"], "y": agg_df["Confirmed"], "name": "Confirmed"},
            {"x": agg_df["ObservationDate"], "y": agg_df["Deaths"], "name": "Deaths"},
            {"x": agg_df["ObservationDate"], "y": agg_df["Recovered"], "name": "Recovered"},
        ],
        "layout": go.Layout(
            colorway=["#5E0DAC", '#FF4F00', '#375CB1',
                      '#FF7400', '#FFF400', '#FF0056'],
            height=600,
            title=f"All cases",
            xaxis={"title": "ObservationDate"},
            yaxis={"title": "Count"})
    }
    return figure


@app.callback(Output('recent-tweets-table', 'children'),
              events=[Event('recent-table-update', 'interval')])
def update_recent_tweets():
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} ORDER BY id DESC LIMIT 10", sql_helper.conn)
    df = df.drop(['id_str'], axis=1)
    df = df[['created_at', 'user_name', 'tweet', 'user_location']]

    return generate_table(df, max_rows=10)


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)
