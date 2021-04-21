import datetime
import traceback
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
from pymongo import InsertOne, MongoClient

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import STOP_WORDS, MONGO_URL, DB_NAME, COVID_TRACK_WORDS, BED_TRACK_WORDS, VENTILATOR_TRACK_WORDS,\
    OXYGEN_TRACK_WORDS
from tools.twitter_utils import de_emojify

bad_words = Counter(dict(zip(STOP_WORDS, [1000000]*len(STOP_WORDS))))
punctuations = [str(i) for i in string.punctuation]
split_regex = re.compile("[ \n" + re.escape("".join(punctuations)) + ']')

mongo = MongoClient(MONGO_URL)[DB_NAME]


class Listener(StreamListener):

    def __init__(self, api=None):
        super().__init__(api=None)
        self.covid_data_list, self.bed_data_list, self.ventilator_data_list, self.oxygen_data_list = [], [], [], []
        self.value_list = []
        self.thresh = 50
        self.trending_thresh = 500
        self.counter, self.trending_counter = 0, 0

    def on_connect(self):
        print("Connected to Twitter API")

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            # Ignore all the retweets
            if tweet["retweeted"] or tweet["text"].startswith("RT"):
                return True

            # Verified or not
            user_verified = tweet["user"]["verified"]

            # Timestamp
            timestamp_ms = int(time.time())
            created_at = tweet["created_at"]

            # location filtering
            user_location = de_emojify(tweet["user"].get("location", ""))
            # Filtering locations to target only Indian Tweets
            if any([loc in user_location.lower() for loc in ['pakistan', 'bangladesh', 'sri lanka', 'afghanistan']]):
                return True

            # User data
            user_name = de_emojify(tweet["user"].get("name", ""))
            screen_name = de_emojify(tweet["user"].get("screen_name", ""))

            # Tweet text
            if not tweet["truncated"]:
                tweet_data = de_emojify(unidecode(tweet["text"]))
                sentiment = TextBlob(tweet_data).sentiment.polarity
            else:
                tweet_data = de_emojify(unidecode(tweet['extended_tweet']['full_text']))
                sentiment = int(TextBlob(tweet_data).sentiment.polarity)

            if sentiment > 0:
                sentiment = "Positive"
            elif sentiment == 0:
                sentiment = "Neutral"
            else:
                sentiment = "Negative"

            print("TEXT-> ", tweet_data)
            print("CREATED_AT-> ", created_at)
            print("USER_LOCATION-> ", user_location)
            print("VERIFIED-> ", user_verified)
            print("SENTIMENT->", sentiment)
            print('---------------------------------------------------------------------\n')

            data_to_insert = {
                "timestamp_ms": timestamp_ms,
                "code": int(time.time()),
                "tweet_data": tweet_data,
                "created_at": created_at,
                "user_location": user_location,
                "user_name": user_name,
                "screen_name": screen_name,
                "user_verified": user_verified,
                "sentiment": sentiment
            }

            # Tweet filtering Logic
            temp_tweet_text = tweet_data.lower()
            if any([word in temp_tweet_text for word in COVID_TRACK_WORDS]):
                self.covid_data_list.append(InsertOne(data_to_insert))
            if any([word in temp_tweet_text for word in BED_TRACK_WORDS]):
                self.bed_data_list.append(InsertOne(data_to_insert))
            if any([word in temp_tweet_text for word in VENTILATOR_TRACK_WORDS]):
                self.ventilator_data_list.append(InsertOne(data_to_insert))
            if any([word in temp_tweet_text for word in OXYGEN_TRACK_WORDS]):
                self.oxygen_data_list.append(InsertOne(data_to_insert))

            self.value_list.append(InsertOne(data_to_insert))
            self.counter += 1
            self.trending_counter += 1

            # Insert all the entries into mongoDB
            if self.counter % self.thresh == 0:
                print("===============Thresh satisfied: Inserting into Mongo DB=====================")
                if self.value_list:
                    mongo['twitter_stream_data'].bulk_write(self.value_list)
                if self.covid_data_list:
                    mongo['twitter_covid_data'].bulk_write(self.covid_data_list)
                if self.bed_data_list:
                    mongo['twitter_bed_data'].bulk_write(self.bed_data_list)
                if self.ventilator_data_list:
                    mongo['twitter_ventilator_data'].bulk_write(self.ventilator_data_list)
                if self.oxygen_data_list:
                    mongo['twitter_oxygen_data'].bulk_write(self.oxygen_data_list)
                self.counter = 0
                self.covid_data_list, self.bed_data_list, self.ventilator_data_list, self.oxygen_data_list = [], [], [], []
                self.value_list = []

                # Trending data generation after 500 entries
                if self.trending_counter % self.trending_thresh == 0:
                    generate_trending()
                    self.trending_counter = 0

        except Exception as e:
            traceback.print_exc()
            # TODO: add Logging
            print("Inside on_data Streaming Exception", str(e))
        return True

    def on_error(self, status_code):
        print(f"Encountered streaming error: {status_code}")
        self.covid_data_list, self.bed_data_list, self.ventilator_data_list, self.oxygen_data_list = [], [], [], []
        self.value_list = []


def generate_trending():
    try:
        deletion_logic = {"code": {"$lt": int(time.time()) - 86400*2}}  # 3 days old remove
        mongo['twitter_stream_data'].remove(deletion_logic)
        mongo['trending_data'].remove(deletion_logic)

        df = pd.DataFrame(list(mongo['twitter_stream_data'].aggregate([
            {"$sort": {"timestamp_ms": -1}}, {"$limit": 2000}])))

        df['nouns'] = df['tweet'].apply(lambda x: [word[0] for word in TextBlob(x).tags if word[1] == u'NNP'])
        tokens = split_regex.split(' '.join(list(itertools.chain.from_iterable(df['nouns'].values.tolist()))).lower())
        trending = (Counter(tokens) - bad_words).most_common(10)

        if trending:
            # print('updating trending')
            trending_data = {
                "timestamp": datetime.datetime.now(),
                "code": int(time.time()),
                "trending": trending
            }
            mongo['trending_data'].insert_one(trending_data)
            print("Trending Updated in DB")

    except Exception as e:
        print("TRENDING", str(e))


if __name__ == "__main__":
    while True:
        try:
            auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            twitter_stream = Stream(auth, Listener())
            twitter_stream.filter(locations=[68.7, 8.4, 97.25, 37.6])
        except Exception as e:
            print(str(e))
            time.sleep(5)
