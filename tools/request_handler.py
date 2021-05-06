import json
import requests

from config import FLASK_HOST


def internal_request(port, method: str, data):
    try:
        result = requests.post(
            f"http://{FLASK_HOST}:{port}/{method}",
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        ).text

        result = json.loads(result)
        return result, True

    except json.JSONDecodeError:
        return "JSON decode error", False
    except Exception as e:
        return str(e), False


def external_vaccine_request(district_id, date_obj, pincode=None):
    api_dict = {
        "state_list": "/v2/admin/location/states",
        "district_list": "/v2/admin/location/districts/",  # /{state_id},
        "appointment_by_pin": "/v2/appointment/sessions/public/findByPin",  # ?pincode=xxxxx&date=xx-xx-xxxx
        "appointment_by_district": "/v2/appointment/sessions/public/findByDistrict",  # ?district_id=xxx&date=xx-xx-xxxx
        "7_day_appointment_by_pin": "/v2/appointment/sessions/public/calendarByPin",  # ?pincode=xxxxx&date=xx-xx-xxxx
        "7_day_appointment_by_district": "/v2/appointment/sessions/public/calendarByDistrict", # ?district_id=xxx&date=xx-xx-xxxx
    }

    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    base_link = 'https://cdn-api.co-vin.in/api'

    try:
        if not pincode:
            result = requests.get(
                base_link + api_dict["7_day_appointment_by_district"] + f"?district_id={district_id}&date={date_obj}",
                headers=header
            )
            result = json.loads(result.text)
        elif pincode and not district_id:
            result = requests.get(
                base_link + api_dict["7_day_appointment_by_pin"] + f"?pincode={pincode}&date={date_obj}",
                headers=header
            )
            result = json.loads(result.text)

        else:
            result = {}

        return result

    except Exception as e:
        return str(e)








