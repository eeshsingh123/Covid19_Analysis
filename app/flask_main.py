import os
import random

from flask import Flask, jsonify, request, render_template, url_for
from flask_pymongo import PyMongo
from pymongo import InsertOne

from config import FLASK_HOST, FLASK_PORT, MONGO_URL, PATHS, TEMPLATES_PATH, STATIC_PATH, COLOR_LIST ,COLOR_DICT
from workers.data_preprocess import GraphDataFormatter
from workers.twitter_operations import TwitterHandler

app = Flask(__name__, template_folder=TEMPLATES_PATH, static_folder=STATIC_PATH)
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

try:
    mongo.db.covid_data.count_documents({"x": 1})
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
        mongo.db.covid_data.count_documents({"x": 1})
        results.append("Database connection is working")
    except Exception as e:
        results.append(f"Database connection not working, Error: {e}")

    return jsonify({"status": "successful", "message": results})


@app.route('/home', methods=["POST", "GET"])
def home():
    daily_result = graph_data_formatter.get_current_days_data()
    time_series_total, time_series_daily = graph_data_formatter.get_time_series_data()

    assert time_series_total, "Time series (Total) data not obtained from `data_preprocess.py`"
    assert time_series_daily, "Time series (Daily) data not obtained from `data_preprocess.py`"
    # Formatting it according to Chart js. (can be formatted according to any other graph libs here..)

    time_series_total_formatted = {
        "labels": time_series_total['data'][0]['x'],
        "datasets": [
            {"data": i["y"], "label": i["name"],
             "borderColor": COLOR_DICT.get(i["name"].split()[1], COLOR_DICT["Other"]),
             "tension": 0.1, "pointBorderWidth": 1, "fill": False, "pointRadius": 0.8}
            for i in time_series_total["data"]
        ]
    }

    time_series_daily_formatted = {
        "labels": time_series_daily['data'][0]['x'],
        "datasets": [
            {"data": j["y"], "label": j["name"],
             "borderColor": COLOR_DICT.get(j["name"].split()[1], COLOR_DICT["Other"]),
             "tension": 0.1, "pointBorderWidth": 1, "fill": False, "pointRadius": 0.8}
            for j in time_series_daily["data"]
        ]
    }

    return render_template(
        'dashboard.html',
        title='Dashboard',
        daily_data=daily_result,
        time_series_total=time_series_total_formatted,
        time_series_daily=time_series_daily_formatted
    )


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)