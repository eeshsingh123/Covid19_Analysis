import datetime
import time
import json

import pymongo
from flask import Flask, jsonify, request, render_template, url_for
from flask_pymongo import PyMongo
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

import numpy as np

from config import FLASK_HOST, FLASK_PORT, MONGO_URL, TEMPLATES_PATH, STATIC_PATH, COLOR_DICT, STATE_LIST, COLOR_LIST, \
    REDIS_CONN, RQ_CHANNELS, DEBUG, BASE_DATA_PATH
from tools.kill_schedules import kill_schedule
from tools.timezone_corrector import get_current_timezone_time
from workers.data_preprocess import GraphDataFormatter
from workers.scheduled_operations import update_reports_and_twitter_endpoints
from workers.twitter_operations import TwitterHandler

app = Flask(__name__, template_folder=TEMPLATES_PATH, static_folder=STATIC_PATH)
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)
RCONN = Redis(**REDIS_CONN)

try:
    mongo.db.twitter_covid_data.count_documents({"x": 1})
    print("Database is Working")
except Exception as ee:
    print("Database not working, Error: ", ee)

graph_data_formatter = GraphDataFormatter()
twitter_handler = TwitterHandler()

if not DEBUG:
    today = datetime.datetime.now()
    Queue(name=RQ_CHANNELS['data_updater'], connection=RCONN).empty()
    print('Queue emptied')
    print('Killing Underlying Schedules', kill_schedule(RQ_CHANNELS['data_updater']))

    sch = Scheduler(RQ_CHANNELS['data_updater'], connection=RCONN).schedule(
        scheduled_time=get_current_timezone_time(datetime.datetime(
            today.year,
            today.month,
            today.day,
            00, 00
        ), time_zone="Asia/Kolkata"),
        func=update_reports_and_twitter_endpoints,
        interval=3600 * 3,  # every 3 hours
        repeat=None
    )
    print("Scheduler ->", sch)

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


@app.route('/update_reports', methods=["GET", "POST"])
def update_reports():
    try:
        global graph_data_formatter, twitter_handler
        graph_data_formatter = GraphDataFormatter()
        twitter_handler = TwitterHandler()

        print("All dataframes updated")

        return jsonify({
            "status": "successful",
            "result": "All dataframes updated successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "erorr",
            "result": str(e)
        })


@app.route('/home', methods=["GET"])
def home():
    try:
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

    except Exception as e:
        date = datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y")
        with open(f"{BASE_DATA_PATH}/logs/error_logs_{date}.txt", "a", encoding="utf-8") as log_fp:
            log_fp.write(
                f"""\n*******************************\n
                 Time: {datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y %H:%M:%S")},\n
                 Function: home()\n
                 Error: {str(e)}\n*******************************\n"""
            )
        return render_template('error.html')


@app.route("/home/<state>", methods=["GET", "POST"])
def state_analysis(state="#"):
    try:
        # Todo: Add try except and template error handling
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

    except Exception as e:
        date = datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y")
        with open(f"{BASE_DATA_PATH}/logs/error_logs_{date}.txt", "a", encoding="utf-8") as log_fp:
            log_fp.write(
                f"""\n*******************************\n
                 Time: {datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y %H:%M:%S")},\n
                 Function: state_analysis()\n
                 Error: {str(e)}\n*******************************\n"""
            )
        return render_template('error.html')


@app.route('/vc/get_center/<state>', methods=["GET", "POST"])
def get_vaccine_centers(state="#"):
    district_dict = graph_data_formatter.state_district_map[state]
    district = request.form.get("district")
    dist = list(district_dict.keys())[0] if not district else district

    RCONN.set(district, str(int(time.time())))

    vaccine_data = graph_data_formatter.get_vaccine_center_data(state_name=state, district_name=dist)

    # To test the data without hitting api multiple times and avoid rate limit
    # with open(f'{BASE_DATA_PATH}/sample_result/sample_res.json', 'r') as fp:
    #     vaccine_data = json.load(fp)

    vaccine_final_data = []
    for i in vaccine_data['centers']:
        vaccine_final_data.append({
            "Pincode": i['pincode'],
            "Center Name": i['name'],
            "Address": i['address'],
            "Locality": i['block_name'],
            "Session Start Time": i['from'],
            "Session End Time": i['to'],
            "Session Fee": i['fee_type'],
            "Sessions": [
                {
                    'Date': s['date'],
                    'Available Capacity': s['available_capacity'],
                    'Min Age Limit': s['min_age_limit'],
                    'Vaccine': s['vaccine'],
                    'Slots': ", ".join(s['slots'])
                } for s in i['sessions']
            ],

        })

    return render_template(
        'vaccine_table.html',
        title='Vaccination Schedule',
        vaccine_data=vaccine_final_data,
        district_dict=district_dict,
        state_list=STATE_LIST,
        current_state=state,
        current_district=dist
    )


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)