import time
import json
from unidecode import unidecode

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from misc.sql_operations import SqlHelper
from tools.emoji_cleaner import de_emojify

sql_helper = SqlHelper()
db_status = sql_helper.create_table()
print(db_status)


class Listener(StreamListener):

    def __init__(self, api=None):
        super().__init__(api=None)
        self.value_list = []
        self.thresh = 10

    def on_connect(self):
        print("Connected to Twitter API")

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            if tweet["retweeted"] or tweet["text"].startswith("RT"):
                return True

            user_verified = tweet["user"]["verified"]
            id_str = tweet["id_str"]
            created_at = tweet["created_at"]
            user_location = de_emojify(tweet["user"].get("location", ""))
            user_name = de_emojify(tweet["user"].get("name", ""))
            screen_name = de_emojify(tweet["user"].get("screen_name", ""))
            if not tweet["truncated"]:
                tweet_data = de_emojify(unidecode(tweet["text"]))
            else:
                tweet_data = de_emojify(unidecode(tweet['extended_tweet']['full_text']))

            print("TEXT-> ", tweet_data)
            print("CREATED_AT-> ", created_at)
            print("USER_LOCATION-> ", user_location)
            print("VERIFIED-> ", user_verified)
            print('---------------------------------------------------------------------\n')

            self.value_list.append((
                id_str, tweet_data, created_at, user_location, user_name, screen_name, user_verified
            ))

            if len(self.value_list) > self.thresh:
                print("thresh satisfied: Inserting into DB", len(self.value_list))
                sql_helper.insert_into_table(values_list=self.value_list)
                self.value_list = []

        except Exception as e:
            print("Inside on_data Streaming Exception", str(e))
            self.value_list = []
        return True

    def on_error(self, status_code):
        print(f"Encountered streaming error: {status_code}")


if __name__ == "__main__":
    while True:
        try:
            auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            twitter_stream = Stream(auth, Listener())

            track = ["Corona", "corona", "Covid-19", "Covid19", "Corona Virus", "corona virus"]
            twitter_stream.filter(track=track, languages=["en"])
        except Exception as e:
            print(str(e))
            time.sleep(5)
