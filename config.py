import os
import json

DEBUG = os.environ.get("DEBUG", True)
LTS = True if not DEBUG else False

if LTS:
    BASE_PATH = os.environ.get("BASE_PATH", os.path.join(os.sep, 'mnt', 'c', 'Projects', 'Python_projects', 'Covid19_Analysis'))
    BASE_DATA_PATH = os.environ.get("BASE_DATA_PATH",
                                    os.path.join(os.sep, 'mnt', 'c', 'Projects', 'Python_projects', 'Covid19_Analysis', 'data'))
else:
    BASE_PATH = os.environ.get("BASE_PATH", os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis'))
    BASE_DATA_PATH = os.environ.get("BASE_DATA_PATH",
                                    os.path.join(os.sep, 'Projects', 'Python_projects', 'Covid19_Analysis', 'data'))
    if not os.path.isdir(BASE_PATH):
        os.mkdir(BASE_DATA_PATH)

RQ_CHANNELS = {'data_updater': 'daily_data_updater'}

REDIS_CONN = {
    "host": os.environ.get("REDIS_HOST", "localhost"),
    "port": os.environ.get("REDIS_PORT", 6379)
}

COVID_TRACK_WORDS = ['corona', 'covid19', 'covid-19', 'pandemic', 'virus', 'vaccine', 'vaccination', 'remdesivir injection', 'remdesivir']

BED_TRACK_WORDS = ['bed', 'beds', 'hospital bed', 'urgent bed', 'hospitals', 'bed shortage',
                   'bed needed', 'beds needed', 'bed help', 'need bed', 'need beds', 'icu beds']

OXYGEN_TRACK_WORDS = ['oxygen', 'oxygen needed', 'need oxygen', 'oxygen need', 'help oxygen', 'oxygen shortage',
                      'hospital oxygen', 'urgent oxygen', 'oxygen help']

VENTILATOR_TRACK_WORDS = [word.replace('oxygen', 'ventilator') for word in OXYGEN_TRACK_WORDS]

TRACKED_USERS = ["@covid19indiaorg", "@COVIDNewsByMIB", "@ANI", "@BloodDonorsIn", "@CovidIndiaSeva", "@MoHFW_INDIA"]
HASHTAG_1 = ['#Help', '#Help', '#Urgent', '#urgent', "Available", "#available"]
HASHTAG_2 = ["#Beds", "#Oxygen", "#Remdesivir", "#Ventilator", "#Crematorium", "#Vaccine"]

STREAM_DATA_KEEP_DAYS = 5
USER_HASHTAG_KEEP_DAYS = 30

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

COLOR_PALETTE = ["#ffcb91", "#ffefa1", "#94ebcd", "#bfcc80"]

COLOR_LIST = ['#AAEBDE', '#9BBFB9', '#8A81BF', '#A9EEA6', '#96CC81',
              '#A78AB0', '#94D1B9', '#D9D2FB', '#D48674', '#D3656F',
              '#AAC5E5', '#D6E7AC', '#D3ACB2', '#C2CD92', '#B3F7BE',
              '#A0828C', '#CEFC8E', '#B97D86', '#AEE971', '#727C83',
              '#E3ACF7', '#9EA3B0', '#F892BB', '#EEFCF9', '#7AC16E',
              '#A8C3DF', '#D5DDF4', '#C1A064', '#83F2FF', '#7EF5B3',
              '#EAF49C', '#8E94D9', '#6E9AF8', '#FFD28A', '#CDC189',
              '#8AA56D', '#BEB37B', '#C9EC75', '#96AD9C', '#CF6CAD',
              '#88FA9D', '#EA8A7C', '#B0F1BC', '#FB8D78', '#FD8871',
              '#F1B582', '#79B164', '#E4E4F3', '#D49673', '#CEE7F7']

COLOR_DICT = {
    "Confirmed": "#B22222",
    "Daily Confirmed": "#DC143C",
    "Deceased": "#87CEEB",
    "Daily Deceased": "#87CEEB",
    "Recovered": "#00FF00",
    "Daily Recovered": "#00FF00",
    "Other": "#FFFAFA"
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

# Removing Excess log files, Limit = 5
sorted_logs = sorted(f"{BASE_DATA_PATH}/logs/")
if len(sorted_logs) > 5:
    os.remove(f"{BASE_DATA_PATH}/logs/{sorted_logs[0]}")

if __name__ == "__main__":
    print(TABLE_ATTRIBUTES["base"])
