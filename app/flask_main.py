import os

from flask import Flask, jsonify
from flask_pymongo import PyMongo
from pymongo import InsertOne

from config import FLASK_HOST, FLASK_PORT, MONGO_URL, PATHS

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

try:
    mongo.db.covid_data.count_documents({"x": 1})
    print("Database is Working")
except Exception as ee:
    print("Database not working, Error: ", ee)

print("-------------------APP IS READY------------------------")


@app.route('/test', methods=["GET"])
def test():
    results = ["Flask app is ready to use"]
    try:
        mongo.db.covid_data.count_documents({"x": 1})
        results.append("Database connection is working")
    except Exception as e:
        results.append(f"Database connection not working, Error: {e}")

    return jsonify({"status": "successful", "message": results})


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)