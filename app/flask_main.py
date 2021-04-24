import os

from flask import Flask, jsonify, request, render_template, url_for
from flask_pymongo import PyMongo
from pymongo import InsertOne

from config import FLASK_HOST, FLASK_PORT, MONGO_URL, PATHS, TEMPLATES_PATH, STATIC_PATH
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

    return render_template(
        'dashboard.html',
        title='Dashboard',
        daily_data=daily_result,
        time_series_total=time_series_total,
        time_series_daily=time_series_daily
    )


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=FLASK_PORT, use_reloader=False)