import os
import json
import secrets

BASE_PATH = "C:\\Projects\\Python_projects\\Covid19_Analysis"

TABLE_NAME = "covid"

TABLE_ATTRIBUTES = {
    "base": """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_str TEXT,
    tweet TEXT,
    created_at TEXT,
    user_location TEXT,
    user_name TEXT,
    screen_name TEXT,
    verified BOOLEAN
    """
}

APP_COLORS = {
    'background': '#0C0F0A',
    'text': '#000000',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

if __name__=="__main__":
    print(TABLE_ATTRIBUTES["base"])