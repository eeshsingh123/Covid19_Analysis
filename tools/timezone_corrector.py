import datetime
import pytz
from tzlocal import get_localzone


def get_current_timezone_time(datetime_object, time_zone=None):
    tz1 = pytz.timezone(time_zone) if time_zone else pytz.timezone(get_localzone().zone)
    tz2 = pytz.timezone("UTC")

    dt = tz1.localize(datetime_object)
    dt = dt.astimezone(tz2)
    dt = datetime.datetime.strptime(dt.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return dt


if __name__ == "__main__":
    today = datetime.datetime.now()
    print(get_current_timezone_time(
        datetime_object=datetime.datetime(today.year, today.month, today.day, 15, 35)
    ))
