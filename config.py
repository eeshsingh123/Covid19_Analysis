import os
import json

DEBUG = os.environ.get("DEBUG", True)
BASE_PATH = os.environ.get("BASE_PATH", os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis'))
BASE_DATA_PATH = os.environ.get("BASE_DATA_PATH", os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis', 'data'))
if not os.path.isdir(BASE_PATH):
    os.mkdir(BASE_DATA_PATH)

COVID_TRACK_WORDS = ['corona', 'covid19', 'covid-19', 'pandemic', 'virus', 'vaccine', 'vaccination', 'remdesivir injection', 'remdesivir']

BED_TRACK_WORDS = ['bed', 'beds', 'hospital bed', 'urgent bed', 'hospitals', 'bed shortage',
                   'bed needed', 'beds needed', 'bed help', 'need bed', 'need beds', 'icu beds']

OXYGEN_TRACK_WORDS = ['oxygen', 'oxygen needed', 'need oxygen', 'oxygen need', 'help oxygen', 'oxygen shortage',
                      'hospital oxygen', 'urgent oxygen', 'oxygen help']

VENTILATOR_TRACK_WORDS = [word.replace('oxygen', 'ventilator') for word in OXYGEN_TRACK_WORDS]

TRACKED_USERS = ["@covid19indiaorg", "@COVIDNewsByMIB", "@ANI"]

STREAM_DATA_KEEP_DAYS = 3
USER_HASHTAG_KEEP_DAYS = 5

SEARCH_BY_HASHTAG = {
    'bed': 'bed',
    'oxygen': 'oxygen',
    'ventilator': 'ventilator'
}

TEMPLATES_PATH = os.environ.get("EDA_TEMPLATES_PATH", os.path.join(os.sep, BASE_PATH, "templates"))
STATIC_PATH = os.environ.get("EDA_STATIC_PATH", os.path.join(os.sep, BASE_PATH, "static"))

FLASK_HOST = os.environ.get('FLASK_HOST', "127.0.0.1")
FLASK_PORT = os.environ.get('FLASK_PORT', 7916)

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

COLOR_LIST = ['#6a2c70', '#b83b5e', '#f08a5d', '#056674', '#16213e', '#1a1a2e', '#0f3460', '#206a5d',
              '#81b214', '#ff8e6e', '#515070', '#6e6d6d', '#ff7171',
              '#f9f437', '#017ac1', '#bfcc80', '#1da07e', '#805854', '#4b7c14', '#a0e769', '#671c93', '#ad7775',
              '#a3427b', '#a86d41', '#fa3709', '#83275d', '#efa15f', '#c9c692', '#720b2d', '#19c983', '#b60902',
              '#27dd7b', '#b1aa89', '#c1e335', '#901a0a', '#91cc96', '#58e81c', '#aca27d', '#19f7c5', '#15d710',
              '#e65dd7', '#84d00e', '#acb75a', '#092df5', '#6cab7c', '#497870', '#6ad4bf', '#8ae58e', '#aff1d5',
              '#1e9f5d', '#1b4b22', '#6188f8', '#8b967a', '#8158ca', '#6fa780', '#e44905', '#8c695d', '#42c745',
              '#6fd048', '#29368d', '#c0f73a', '#50fd22', '#f1e213', '#cc9d6e', '#c247f6', '#39e50e', '#6deb0b',
              '#523b0f', '#685ee5', '#0307da', '#41cfd8', '#9d97f2', '#36efcd', '#89805b', '#7a5291', '#19e7a3',
              '#1dc416', '#4c6239', '#4facee', '#7fb6fe', '#6f9a73', '#e062a8', '#d65434', '#a8f628', '#272e05',
              '#fc3e44', '#ab2917', '#a3c9cc', '#bdeec8', '#b65e1e', '#e9a495', '#e1d024', '#02ee76', '#10e926',
              '#110ae9', '#0935cc', '#c6bee1', '#40af16', '#d149ed', '#3c2089', '#c034cb', '#bb5804', '#2697c9',
              '#2dacd9', '#7f5bfb', '#39d0ce', '#cc0545', '#f61ceb', '#7d785f', '#d08938', '#8f5306', '#791be6',
              '#1b01dd']

COLOR_DICT = {
    "Confirmed": "#B22222",
    "Deceased": "#9884b5",
    "Recovered": "#00FF7F",
    "Other": "#E6E6FA"
}

STATE_LIST = [
 'Maharashtra',
 'Kerala',
 'Karnataka',
 'Andhra Pradesh',
 'Tamil Nadu',
 'Delhi',
 'Uttar Pradesh',
 'West Bengal',
 'Odisha',
 'Rajasthan',
 'Chhattisgarh',
 'Telangana',
 'Haryana',
 'Gujarat',
 'Bihar',
 'Madhya Pradesh',
 'Assam',
 'Punjab',
 'Jammu and Kashmir',
 'Jharkhand',
 'Uttarakhand',
 'Himachal Pradesh',
 'Goa',
 'Puducherry',
 'Tripura',
 'Manipur',
 'Chandigarh',
 'Arunachal Pradesh',
 'Meghalaya',
 'Nagaland',
 'Ladakh',
 'Sikkim',
 'Andaman and Nicobar Islands',
 'Mizoram',
 'Dadra and Nagar Haveli and Daman and Diu',
 'Lakshadweep',
 'State Unassigned'
]

VACCINE_GRAPH_COLS = [
       'Total Individuals Registered', 'First Dose Administered',
       'Second Dose Administered', 'Male', 'Female', 'Transgender',
       'Total Covaxin Administered', 'Total CoviShield Administered',
       'Total Doses Administered', 'delta_total_individuals_registered',
       'delta_first_dose_administered', 'delta_second_dose_administered',
       'delta_male', 'delta_female', 'delta_transgender',
       'delta_total_covaxin_administered',
       'delta_total_covishield_administered',
       'delta_total_doses_administered'
]

if __name__ == "__main__":
    print(TABLE_ATTRIBUTES["base"])
