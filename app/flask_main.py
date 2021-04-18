import os

from flask import Flask, jsonify

from config import FLASK_HOST, FLASK_PORT

app = Flask(__name__)


@app.route('/test', methods=["GET"])
def test():
    return jsonify({"status": "successful", "message": "Flask app is ready to use"})


if __name__ == "__main__":
    app.run(debug=True, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)