import time

import tweepy
from tweepy import OAuthHandler
from pymongo import InsertOne, MongoClient

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import MONGO_URL, DB_NAME, SEARCH_BY_HASHTAG

mongo = MongoClient(MONGO_URL)[DB_NAME]


class TwitterHandler:
    def __init__(self):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_user_timeline(self, user_id: str, count: int):
        data_to_insert = []
        tweets = self.api.user_timeline(
            screen_name=user_id,
            include_rts=False,
            tweet_mode='extended',
            exclude_replies=True,
            count=count
        )

        for t_, tweet_text in enumerate(tweets):
            tweet_dict = {
                "name": tweet_text.user.get('name', user_id),
                "mined_at": int(time.time()),
                "created_at": tweet_text.created_at,
                "text": tweet_text.full_text,
                "retweet_count": tweet_text.retweet_count,
                "favourite_count": tweet_text.favourite_count,
                "hashtags": tweet_text.entities.get("hashtags", []),
                "source": tweet_text.source
            }
            data_to_insert.append(InsertOne(tweet_dict))

        mongo['user_timeline_data'].bulk_write(data_to_insert)
        return True

    def get_tweets_from_hashtag(self, hashtag: str, count: int):
        place = self.api.geo_search(query="India", granularity="country")
        place_id = place[0].id
        data_to_insert = []

        for tweet in tweepy.Cursor(self.api.search, q=f"place:{place_id} #{SEARCH_BY_HASHTAG[hashtag]}").items(count):
            hashtag_tweet_dict = {
                "mined_at": int(time.time()),
                "text": tweet.text,
                "created_at": tweet.created_at
            }
            data_to_insert.append(InsertOne(hashtag_tweet_dict))

        mongo['hashtag_specific_data'].bulk_write(data_to_insert)
        return True
