import time
import json
import string
import re
import itertools
from unidecode import unidecode
from collections import Counter

import pandas as pd
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from textblob import TextBlob

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import STOP_WORDS, TABLE_NAME
from misc.sql_operations import SqlHelper
from tools.emoji_cleaner import de_emojify

sql_helper = SqlHelper()
db_status = sql_helper.create_table()
print(db_status)

bad_words = Counter(dict(zip(STOP_WORDS, [1000000]*len(STOP_WORDS))))
punctuations = [str(i) for i in string.punctuation]
split_regex = re.compile("[ \n" + re.escape("".join(punctuations)) + ']')


class Listener(StreamListener):

    def __init__(self, api=None):
        super().__init__(api=None)
        self.value_list = []
        self.thresh = 10
        self.counter = 0

    def on_connect(self):
        print("Connected to Twitter API")

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            if tweet["retweeted"] or tweet["text"].startswith("RT"):
                return True

            user_verified = tweet["user"]["verified"]
            timestamp_ms = int(time.time())
            created_at = tweet["created_at"]
            user_location = de_emojify(tweet["user"].get("location", ""))
            user_name = de_emojify(tweet["user"].get("name", ""))
            screen_name = de_emojify(tweet["user"].get("screen_name", ""))
            if not tweet["truncated"]:
                tweet_data = de_emojify(unidecode(tweet["text"]))
                sentiment = TextBlob(tweet_data).sentiment.polarity
            else:
                tweet_data = de_emojify(unidecode(tweet['extended_tweet']['full_text']))
                sentiment = TextBlob(tweet_data).sentiment.polarity

            print("TEXT-> ", tweet_data)
            print("CREATED_AT-> ", created_at)
            print("USER_LOCATION-> ", user_location)
            print("VERIFIED-> ", user_verified)
            print("SENTIMENT->", sentiment)
            print('---------------------------------------------------------------------\n')

            self.value_list.append((
                timestamp_ms, tweet_data, created_at, user_location, user_name, screen_name, user_verified, sentiment
            ))
            self.counter += 1
            if self.counter % 2000 == 0:
                self.counter = 0
                generate_trending()

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


def generate_trending():
    try:
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} ORDER BY id DESC LIMIT 2000", sql_helper.conn)
        df['nouns'] = df['tweet'].apply(lambda x: [word[0] for word in TextBlob(x).tags if word[1] == u'NNP'])
        tokens = split_regex.split(' '.join(list(itertools.chain.from_iterable(df['nouns'].values.tolist()))).lower())
        trending = (Counter(tokens) - bad_words).most_common(10)

        if trending:
            # print('updating trending')
            sql_helper.replace_into_trending_table(trending)

    except Exception as e:
        print("TRENDING", str(e))


if __name__ == "__main__":
    while True:
        try:
            auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            twitter_stream = Stream(auth, Listener())

            track = [
                "Corona",
                "corona",
                "Covid-19",
                "Covid19",
                "Corona Virus",
                "corona virus",
                "Covid 19",
                "Vaccine",
                "World Health Organization"
            ]
            twitter_stream.filter(track=track, languages=["en"])
        except Exception as e:
            print(str(e))
            time.sleep(5)
