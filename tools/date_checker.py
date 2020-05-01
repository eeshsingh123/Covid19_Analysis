import datetime
import json

from config import BASE_PATH
from misc.update_daily_data import download_data_from_kaggle
from misc.dbclean_daily import clean_db_daily


def check_date_validity(today):
    try:
        current_day = today.day
        with open(f"{BASE_PATH}\\misc\\last_updated.json", 'r') as fp:
            saved_day = json.load(fp)
        last_updated_day = datetime.datetime.strptime(saved_day['last_updated'], "%d-%m-%Y %H:%M:%S").day

        if abs(current_day - last_updated_day) >= 1:
            print("One day passed, updating new data")
            new_update_day = {"last_updated": datetime.datetime.strftime(today, "%d-%m-%Y %H:%M:%S")}
            with open(f"{BASE_PATH}\\misc\\last_updated.json", 'w') as fp:
                json.dump(new_update_day, fp)
            download_data_from_kaggle()
            clean_db_daily()
    except Exception as e:
        return {
            "status": "error",
            "reason": e
        }
    return {
        "status": "successful",
        "new_date": saved_day['last_updated']
    }
