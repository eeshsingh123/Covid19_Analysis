import os
import json

DEBUG = os.environ.get("DEBUG", True)
BASE_PATH = os.environ.get("BASE_PATH", os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis'))
BASE_DATA_PATH = os.environ.get("BASE_DATA_PATH", os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis', 'data'))
if not os.path.isdir(BASE_PATH):
    os.mkdir(BASE_DATA_PATH)

TEMPLATES_PATH = os.environ.get("EDA_TEMPLATES_PATH", os.path.join(os.sep, BASE_PATH, "templates"))
STATIC_PATH = os.environ.get("EDA_STATIC_PATH", os.path.join(os.sep, BASE_PATH, "static"))

FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = os.environ.get('FLASK_PORT', '7916')

MONGO_DB = {
    "host": "localhost",
    "port": "27017",
    "user": "admin",
    "password": "dbpass123",
    "db": "covid_db"
}

MONGO_URL_ADMIN = f"mongodb://{MONGO_DB['user']}:{MONGO_DB['password']}@{MONGO_DB['host']}:{MONGO_DB['port']}/admin"
DB_NAME = MONGO_DB['db']
MONGO_URL = f"mongodb://{MONGO_DB['user']}:{MONGO_DB['password']}@{MONGO_DB['host']}:{MONGO_DB['port']}/" \
            + DB_NAME + "?authSource=admin"

# Loading default objects
with open(os.path.join(os.sep, BASE_DATA_PATH, 'default_objects', 'stopword_collection.json'), 'r') as stp:
    STOP_WORDS = json.load(stp)

with open(os.path.join(os.sep, BASE_DATA_PATH, 'default_objects', 'country_codes.json'), 'r') as cc:
    COUNTRY_CODE = json.load(cc)

with open(os.path.join(os.sep, BASE_DATA_PATH, 'default_objects', 'country_iso_2_1_conversion.json'), 'r') as cio:
    convert_ISO_3166_2_to_1 = json.load(cio)

with open(os.path.join(os.sep, BASE_DATA_PATH, 'default_objects', 'state_code_mapper.json'), 'r') as sc:
    STATE_CODE_MAPPER = json.load(sc)

PATHS = {
    "time_series_df": "https://api.covid19india.org/csv/latest/case_time_series.csv",
    "states": {
        "state_total": "https://api.covid19india.org/csv/latest/state_wise.csv",
        "state_daily": "https://api.covid19india.org/csv/latest/states.csv",
    },
    "districts": {
        "district_total": "https://api.covid19india.org/csv/latest/district_wise.csv",
        "district_daily": "https://api.covid19india.org/csv/latest/districts.csv",
    },

    "vaccination": {
        "state_daily": "http://api.covid19india.org/csv/latest/cowin_vaccine_data_statewise.csv",
        "state_total": "http://api.covid19india.org/csv/latest/vaccine_doses_statewise.csv"
    }
}

# OLD DASH BASED PROJECT CODE
TABLE_NAME = "covid"
TRENDING_TABLE_NAME = "trending"
POS_NEG_NEUT = 0.1

TABLE_ATTRIBUTES = {
    "base": """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_ms INTEGER,
    tweet TEXT,
    created_at TEXT,
    user_location TEXT,
    user_name TEXT,
    screen_name TEXT,
    verified BOOLEAN,
    sentiment REAL
    """
}

APP_COLORS = {
    'background': '#F0F0F7',
    'text': '#000000',
    'sentiment-plot': '#41EAD4',
    'volume-bar': '#FBFC74',
    'someothercolor': '#9cc0e7',
}

SENTIMENT_COLORS = {
    -1: "#EE6055",
    -0.5: "#FDE74C",
    0: "#FFE6AC",
    0.5: "#D0F2DF",
    1: "#9CEC5B"
}



if __name__ == "__main__":
    print(TABLE_ATTRIBUTES["base"])
