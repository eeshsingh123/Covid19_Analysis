import time
import datetime

from misc.sql_operations import SqlHelper

DATA_DAYS_KEEP = 1
current_ms_time = time.time()*1000
one_day = 86400 * 1000
DATA_TO_DELETE = int(current_ms_time - (DATA_DAYS_KEEP*one_day))


def clean_db_daily():
    sql_helper = SqlHelper()
    delete_status = sql_helper.delete_data_from_db(DATA_TO_DELETE)
    return delete_status
