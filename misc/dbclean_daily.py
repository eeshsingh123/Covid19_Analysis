import time

from misc.sql_operations import SqlHelper

DATA_COUNT_TO_DELETE = 10000


def clean_db_daily():
    sql_helper = SqlHelper()
    delete_status = sql_helper.delete_data_from_db(DATA_COUNT_TO_DELETE)
    return delete_status
