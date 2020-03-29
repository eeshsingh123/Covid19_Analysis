import os
import json
import secrets

BASE_PATH = "C:\\Projects\\Python_projects\\covid_19_analysis"

TABLE_NAME = "covid"

TABLE_ATTRIBUTES = {
    "base": """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_str TEXT,
    tweet TEXT,
    created_at TEXT,
    user_location TEXT,
    geo_data TEXT,
    coordinates TEXT,
    place TEXT,
    retweet_count INTEGER,
    like_count INTEGER,
    verified BOOLEAN
    """
}


if __name__=="__main__":
    print(TABLE_ATTRIBUTES["base"])