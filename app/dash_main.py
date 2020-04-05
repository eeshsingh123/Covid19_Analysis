import pickle
import datetime
import json
from collections import Counter

import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import plotly.graph_objs as go
from rq_scheduler import Scheduler

from misc.update_daily_data import download_data_from_kaggle
from misc.dbclean_daily import clean_db_daily
from misc.sql_operations import SqlHelper
from config import APP_COLORS, BASE_PATH, TABLE_NAME, TRENDING_TABLE_NAME, SENTIMENT_COLORS
from tools.date_checker import check_date_validity
from tools.generate_table import generate_table

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

today = datetime.datetime.now()
status_dict = check_date_validity(today)
if not status_dict.get("status", "") == "successful":
    print("Error in data Update ->", status_dict.get("reason", ""))

sql_helper = SqlHelper()
covid_data = pd.read_csv(f"{BASE_PATH}\\twitter_db\\kaggle_data\\covid_19_data.csv")
covid_data["ObservationDate"] = pd.to_datetime(covid_data["ObservationDate"])
covid_data["Last Update"] = pd.to_datetime(covid_data["Last Update"])

most_common_countries = [k for k, _ in Counter(covid_data["Country/Region"]).most_common(150)]

app.layout = html.Div([
    html.Div([
        html.H1("COVID-19 Dashboard", style={"textAlign": "center"}),
        html.Label(f"Last Updated: {status_dict.get('new_date', today)}", style={"textAlign": "center", "opacity": 0.5}),
        dcc.Graph(id="master-data-display")
    ]),

    html.Div([
        html.Div([
            html.H2("County specific data"),
            dcc.Dropdown(
                id="dropdown-countries",
                options=[{"label": i, "value": i} for i in most_common_countries],
                value=['Mainland China', 'US'],
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
            html.H2("All data for a Country"),
            dcc.Dropdown(
                id="dropdown-1-country",
                options=[{"label": i, "value": i} for i in most_common_countries],
                value="Mainland China",
                multi=False
            ),
            dcc.RadioItems(
                id="radio-graph-type",
                options=[{"label": i, "value": i} for i in ["Linear", "Logarithmic"]],
                value="Linear",
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id="all-3-graph")
        ], className="six columns"),
    ], className="row"),

    html.Div(className="row", children=[
        html.H2("Recent Trending Terms", style={"textAlign": "center"}),
        dcc.Graph(id='recent-trending-data', style={'margin-right': '15px'})
    ]),

    html.Div(className='row', children=[
        html.Div(children=[
            html.H3("Live Tweets from around the World"),
            html.Div(id="recent-tweets-table-unverified"),
        ], className='six columns'),
        html.Div(children=[
            html.H3("Live Tweets from Verified Users"),
            html.Div(id="recent-tweets-table-verified"),
        ], className='six columns')
    ]),

    dcc.Interval(
        id='master-data-event',
        interval=60 * 1000,
        n_intervals=0
    ),

    dcc.Interval(
        id='recent-table-update-unverified',
        interval=5 * 1000,
        n_intervals=0
    ),
    dcc.Interval(
        id='recent-table-update-verified',
        interval=5 * 1000,
        n_intervals=0
    ),
    dcc.Interval(
        id="daily-trending",
        interval=2 * 1000,
        n_intervals=0
    )],
    style={"background-color": APP_COLORS["background"]},

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
                  colorway=["#5E0DAC", '#FF4F00', '#37B153',
                            '#FF7400', '#F542C5', '#AAF542'],
                  height=600,
                  title=f"Covid-19 {display_type} cases",
                  xaxis={"title": "ObservationDate"},
                  yaxis={"title": display_type}
              )}
    return figure


@app.callback(Output(component_id='all-3-graph', component_property='figure'),
              [Input(component_id='dropdown-1-country', component_property='value'),
               Input(component_id='radio-graph-type', component_property='value')])
def display_all_data(country, gtype):
    agg_df = covid_data[covid_data["Country/Region"] == country].groupby("ObservationDate").agg(
        {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}).reset_index()
    figure = {
        "data": [
            {"x": agg_df["ObservationDate"], "y": agg_df["Confirmed"], "name": "Confirmed"},
            {"x": agg_df["ObservationDate"], "y": agg_df["Deaths"], "name": "Deaths"},
            {"x": agg_df["ObservationDate"], "y": agg_df["Recovered"], "name": "Recovered"},
        ] if gtype == "Linear" else [
            {"x": agg_df["ObservationDate"], "y": np.log1p(agg_df["Confirmed"]), "name": "Confirmed"},
            {"x": agg_df["ObservationDate"], "y": np.log1p(agg_df["Deaths"]), "name": "Deaths"},
            {"x": agg_df["ObservationDate"], "y": np.log1p(agg_df["Recovered"]), "name": "Recovered"},
        ],
        "layout": go.Layout(
            colorway=["#5E0DAC", '#FF4F00', '#37B153',
                      '#FF7400', '#FFF400', '#FF0056'],
            height=600,
            title=f"All cases",
            xaxis={"title": "ObservationDate"},
            yaxis={"title": "Count"})
    }
    return figure


@app.callback(Output('recent-tweets-table-unverified', 'children'),
              [Input('recent-table-update-unverified', 'n_intervals')])
def update_recent_tweets_unverified(input_data):
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} ORDER BY id DESC LIMIT 5", sql_helper.conn)
    df = df.drop(['id_str'], axis=1)
    df = df[df["verified"] == 0]
    df = df[['created_at', 'user_name', 'tweet', 'user_location', 'sentiment']]
    df.columns = ["Date", "Username", "Tweet", "Tweeted Location", "Sentiment"]
    return generate_table(df, max_rows=8)


@app.callback(Output('recent-tweets-table-verified', 'children'),
              [Input('recent-table-update-verified', 'n_intervals')])
def update_recent_tweets_verified(input_data):
    df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} ORDER BY id DESC LIMIT 1000", sql_helper.conn)
    df = df.drop(['id_str'], axis=1)
    df = df[df["verified"] == 1].iloc[:5, :]
    df = df[['created_at', 'user_name', 'tweet', 'user_location', 'sentiment']]
    df.columns = ["Date", "Username", "Tweet", "Tweeted Location", "Sentiment"]
    return generate_table(df, max_rows=8, is_master=False)


@app.callback(Output('master-data-display', 'figure'),
              [Input('master-data-event', 'n_intervals')])
def display_master_data(input_data):
    master_data = {}
    dff = covid_data.groupby("ObservationDate").agg(
        {"Confirmed": "sum", "Deaths": "sum", "Recovered": "sum"}).reset_index()
    master_data["Confirmed"] = dff.iloc[-1, 1].astype(int)
    master_data["Deaths"] = dff.iloc[-1, 2].astype(int)
    master_data["Recovered"] = dff.iloc[-1, 3].astype(int)

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=master_data["Confirmed"],
        title={
            "text": "Confirmed"},
        domain={'x': [0, 0.2], 'y': [0, 1]},
        delta={'reference': int(dff.iloc[-2, 1]), 'relative': True, }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=master_data["Deaths"],
        title={
            "text": "Deaths"},
        delta={'reference': int(dff.iloc[-2, 2]), 'relative': True},
        domain={'x': [0.4, 0.6], 'y': [0, 1]}))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=master_data["Recovered"],
        title={
            "text": "Recovered"},
        delta={'reference': int(dff.iloc[-2, 3]), 'relative': True},
        domain={'x': [0.8, 1], 'y': [0, 1]}))

    return fig


@app.callback(Output(component_id="recent-trending-data", component_property="figure"),
              [Input(component_id="daily-trending", component_property="n_intervals")])
def update_trending_data(input_data):
    try:
        sql_query = f"SELECT value from {TRENDING_TABLE_NAME} WHERE key='trending'"
        cursor = sql_helper.conn.cursor()
        result = cursor.execute(sql_query).fetchone()
        related_terms = pickle.loads(result[0])

        fig = go.Figure(data=[go.Table(
            cells=dict(values=[t[0] for t in related_terms],
                       fill_color='lavender',
                       align='center',
                       font=dict(color='black', size=25),
                       height=50
                       ))
        ],
            layout={
                "autosize": True,
                "height": 300
            }

        )
        fig.layout['template']['data']['table'][0]['header']['fill']['color'] = 'rgba(0,0,0,0)'
        return fig

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    app.run_server(debug=True, port=7663)
