import time
import sqlite3
from config import BASE_PATH, TABLE_ATTRIBUTES, TABLE_NAME


class SqlHelper:

    def __init__(self):
        try:
            self.conn = sqlite3.connect(
                f"{BASE_PATH}//twitter_db//twitter_data.db",
                isolation_level=None,
                check_same_thread=False
            )
            self.cursor = None
        except Exception as e:
            print("Database Connection Error", e)

    def create_table(self):
        self.cursor = self.conn.cursor()

        print("Creating Table")
        self.cursor.execute("PRAGMA journal_mode=wal")
        self.cursor.execute("PRAGMA wal_checkpoint=TRUNCATE")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}({TABLE_ATTRIBUTES['base']})""")
        self.cursor.execute(f"""CREATE INDEX IF NOT EXISTS fast_tweet on {TABLE_NAME}(tweet)""")
        self.cursor.execute(f"""CREATE INDEX IF NOT EXISTS fast_id_str on {TABLE_NAME}(id_str)""")
        self.conn.commit()
        self.cursor.close()

        return True

    def insert_into_table(self, values_list):
        self.cursor = self.conn.cursor()
        sql_query = f"""INSERT INTO {TABLE_NAME}(id_str, tweet, created_at, user_location, user_name, screen_name, verified)
                        VALUES(?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.executemany(sql_query, values_list)
        print("Bulk insert complete")
        self.conn.commit()
        self.cursor.close()

    # BE CAUTIOUS WHILE USING THIS
    def drop_table(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""DROP TABLE {TABLE_NAME}""")
        self.conn.commit()
        self.cursor.close()


if __name__ == "__main__":
    sq = SqlHelper()
    sq.insert_into_table([("1", "2", "3", "4", "5", "6", "7", 1,2,True), ("1", "2", "3", "4", "5", "6", "7", 1,2,True), ("1", "2", "3", "4", "5", "6", "7", 1,2,True)])