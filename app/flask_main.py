import random

import pymongo
from flask import Flask, jsonify, request, render_template, url_for
from flask_pymongo import PyMongo
import numpy as np

from config import FLASK_HOST, FLASK_PORT, MONGO_URL, TEMPLATES_PATH, STATIC_PATH, COLOR_DICT, STATE_LIST,\
    VACCINE_GRAPH_COLS, COLOR_LIST
from workers.data_preprocess import GraphDataFormatter
from workers.twitter_operations import TwitterHandler

app = Flask(__name__, template_folder=TEMPLATES_PATH, static_folder=STATIC_PATH)
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

try:
    mongo.db.twitter_covid_data.count_documents({"x": 1})
    print("Database is Working")
except Exception as ee:
    print("Database not working, Error: ", ee)

graph_data_formatter = GraphDataFormatter()
twitter_handler = TwitterHandler()

print("*-------------------APP IS READY------------------------*")


@app.route('/', methods=["GET", "POST"])
def test():
    results = ["Flask app is ready to use"]
    try:
        mongo.db.twitter_covid_data.count_documents({"x": 1})
        results.append("Database connection is working")
    except Exception as e:
        results.append(f"Database connection not working, Error: {e}")

    return jsonify({"status": "successful", "message": results})


@app.route('/home', methods=["POST", "GET"])
def home():
    # DATA LOADING
    daily_result = graph_data_formatter.get_current_days_data()
    time_series_total, time_series_daily = graph_data_formatter.get_time_series_data()
    state_vaccine_daily, state_vaccine_agg = graph_data_formatter.get_vaccine_data(state="India")
    top_states_total = graph_data_formatter.get_top_states_data(top=10)

    # EXTRACTING DATA FROM MongoDB
    covid_twitter_data = list(mongo.db.twitter_stream_data.find({}).sort('code', pymongo.DESCENDING).limit(50))
    hashtag_twitter_data = list(mongo.db.hashtag_specific_data.find({}).sort('mined_at', pymongo.DESCENDING).limit(100))
    user_specific_data = list(mongo.db.user_timeline_data.find({}).sort('mined_at', pymongo.DESCENDING))
    twitter_trending_data = list(mongo.db.trending_data.find({}).sort('code', pymongo.DESCENDING).limit(1))

    assert time_series_total, "Time series (Total) data not obtained from `data_preprocess.py`"
    assert time_series_daily, "Time series (Daily) data not obtained from `data_preprocess.py`"
    # Formatting it according to Chart js. (can be formatted according to any other graph libs here..)

    # TWITTER DATA
    # trending data preprocessing
    trend_format = []
    for trend_d in twitter_trending_data:
        for trend_l in trend_d['trending']:
            trend_format.append({"word": str(trend_l[0]), "size": str(trend_l[1] * 9)})

    final_trend_format = {
        "chart_id": "trend-wordcloud-1",
        "chart_data": trend_format
    }

    # user timeline data formatting
    tracked_users_dict = {}
    for user_data in user_specific_data:
        if user_data['name'] not in tracked_users_dict:
            tracked_users_dict[user_data['name']] = [{
                "created_at": user_data['created_at'],
                "text": user_data['text'],
                "hashtags": user_data['hashtags']
            }]
        else:
            tracked_users_dict[user_data['name']].append({
                "created_at": user_data['created_at'],
                "text": user_data['text'],
                "hashtags": user_data['hashtags']
            })

    # TIME SERIES OF CASES DATA FORMATTING
    time_series_total_formatted = {
        "labels": time_series_total['data'][0]['x'],  # The date column
        "datasets": [
            {"data": i["y"], "label": i["name"],
             "borderColor": COLOR_DICT.get(i["name"].split()[1], COLOR_DICT["Other"]),
             "tension": 0.1, "pointBorderWidth": 0.2, "borderWidth":1.8, "fill": False, "pointRadius": 1}
            for i in time_series_total["data"]
        ]
    }

    time_series_daily_formatted = {
        "labels": time_series_daily['data'][0]['x'],
        "datasets": [
            {"data": j["y"], "label": j["name"],
             "borderColor": COLOR_DICT.get(j["name"].split()[1], COLOR_DICT["Other"]),
             "tension": 0.1, "pointBorderWidth": 0.2, "borderWidth":1.8, "fill": False, "pointRadius": 1}
            for j in time_series_daily["data"]
        ]
    }

    # VACCINATION DATA PREPROCESSING
    vaccine_data = []
    final_formatted_vaccine_data = []

    for vaccine_chart_type in [co for co in state_vaccine_daily['data'] if co not in ['Updated On', 'State', 'AEFI']]:
        vaccine_data.append({
            vaccine_chart_type: [{
                "data": state_vaccine_daily['data'][vaccine_chart_type],
                "label": vaccine_chart_type,
                "borderColor": list(np.random.choice(COLOR_LIST, 1, replace=False))[0],
                "tension": 0.1,
                "pointBorderWidth": 1,
                "fill": False,
                "pointRadius": 1
            }]
        })

    for c_, col_combination in enumerate([
        ('Total Sessions Conducted', 'Total Doses Administered'),
        ('delta_total_sessions_conducted', 'delta_total_doses_administered'),
        ('First Dose Administered', 'Second Dose Administered'),
        ('delta_first_dose_administered', 'delta_second_dose_administered'),
        ('Total Covaxin Administered', 'Total CoviShield Administered'),
        ('delta_total_covaxin_administered', 'delta_total_covishield_administered'),
        ('Male', 'Female', 'Transgender'),
        ('delta_male', 'delta_female', 'delta_transgender')
    ]):
        final_formatted_vaccine_data.append({
            "chart_id": f"vac_{c_+100}",
            "chart_name": " V/S ".join([c.replace('_', " ") for c in col_combination]).title(),
            "chart_data": {
                "labels": state_vaccine_daily['data']['Updated On'],
                "datasets": [j[i][0] for j in vaccine_data for i in col_combination if
                             i in j]
            }
        })

    # making agg data user friendly
    vac_agg_fn = {}
    for k, v in state_vaccine_agg.items():
        k = k.replace('Total', "").strip()
        if k.startswith('delta'):
            k = " ".join(k.split("_"))
            k = k.replace("delta", "").strip()
            k = f"{k} Per Day".title()

        vac_agg_fn[k] = v

    return render_template(
        'dashboard.html',
        title='Dashboard',
        daily_data=daily_result,
        time_series_total=time_series_total_formatted,
        time_series_daily=time_series_daily_formatted,
        covid_twitter_data=covid_twitter_data,
        hashtag_twitter_data=hashtag_twitter_data,
        user_specific_data=tracked_users_dict,
        vaccine_data=final_formatted_vaccine_data,
        top_states_total=top_states_total,
        vaccine_agg=vac_agg_fn,
        state_list=STATE_LIST,
        trending_data=final_trend_format
    )


@app.route("/home/<state>", methods=["GET", "POST"])
def state_analysis(state="#"):
    state_total, state_daily = graph_data_formatter.get_state_wise_data(state=state)
    state_vaccine_daily, state_vaccine_agg = graph_data_formatter.get_vaccine_data(state=state)

    # structuring State data into chart-js display format
    label = state_daily['data'][0]['x']
    state_graphs = []
    for chart_type in state_daily['data']:
        state_graphs.append({
            "chart_id": chart_type["name"],
            "chart_data": {
                "labels": label,
                "datasets": [{
                    "data": chart_type["y"],
                    "label": chart_type["name"],
                    "borderColor": COLOR_DICT.get(chart_type["name"].split()[0], COLOR_DICT.get(chart_type["name"], COLOR_DICT['Other'])),
                    "tension": 0,
                    "pointBorderWidth": 0.2,
                    "borderWidth":1.8,
                    "fill": False,
                    "pointRadius": 1
                }]
            }
        })

    # Structuring Vaccine data into chart-js display format

    # STATE VACCINE DAILY
    vaccine_data = []
    final_formatted_vaccine_data = []

    for vaccine_chart_type in [co for co in state_vaccine_daily['data'] if co not in ['Updated On', 'State']]:
        vaccine_data.append({
            vaccine_chart_type: [{
                "data": state_vaccine_daily['data'][vaccine_chart_type],
                "label": vaccine_chart_type,
                "borderColor": list(np.random.choice(COLOR_LIST, 1, replace=False))[0],
                "tension": 0.1,
                "pointBorderWidth": 0.2,
                "borderWidth": 1.9,
                "fill": False,
                "pointRadius": 1
            }]
        })

    for c_, col_combination in enumerate([
        ('Total Individuals Registered', 'Total Doses Administered'),
        ('delta_total_individuals_registered', 'delta_total_doses_administered'),
        ('First Dose Administered', 'Second Dose Administered'),
        ('delta_first_dose_administered', 'delta_second_dose_administered'),
        ('Total Covaxin Administered', 'Total CoviShield Administered'),
        ('delta_total_covaxin_administered', 'delta_total_covishield_administered'),
        ('Male', 'Female', 'Transgender'),
        ('delta_male', 'delta_female', 'delta_transgender')
    ]):

        final_formatted_vaccine_data.append({
            "chart_id": f"vac_{c_}",
            "chart_name": " V/S ".join([c.replace('_', " ") for c in col_combination]).title(),
            "chart_data": {
                "labels": state_vaccine_daily['data']['Updated On'],
                "datasets": [j[i][0] for j in vaccine_data for i in col_combination if
                             i in j]
            }
        })

    vac_agg_fn = {}
    for k, v in state_vaccine_agg.items():
        k = k.replace('Total', "").strip()
        if k.startswith('delta'):
            k = " ".join(k.split("_"))
            k = k.replace("delta", "").strip()
            k = f"{k} Per Day".title()

        vac_agg_fn[k] = v

    return render_template(
        'statewise.html',
        title='Dashboard',
        daily_data=state_total,
        state_daily=state_graphs,
        state_list=STATE_LIST,
        current_state=state,
        vaccine_data=final_formatted_vaccine_data,
        vaccine_agg=vac_agg_fn
    )


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)