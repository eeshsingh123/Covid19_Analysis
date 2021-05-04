import time
import json
import random

import tweepy
from tweepy import OAuthHandler
from pymongo import InsertOne, MongoClient
from tqdm import tqdm

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import MONGO_URL, DB_NAME, USER_HASHTAG_KEEP_DAYS

mongo = MongoClient(MONGO_URL)[DB_NAME]


class TwitterHandler:
    def __init__(self):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        # delete records older than a day
        deletion_logic = {"mined_at": {"$lt": int(time.time()) - 86400 * USER_HASHTAG_KEEP_DAYS}}
        mongo['user_timeline_data'].remove(deletion_logic)
        mongo['hashtag_specific_data'].remove(deletion_logic)

    def get_user_timeline(self, user_id: str, count: int):
        data_to_insert = []
        tweets = []
        tweets_obj = self.api.user_timeline(
            screen_name=user_id,
            include_rts=False,
            tweet_mode='extended',
            exclude_replies=True,
            count=count
        )
        for tweet_data in tweets_obj:
            d = json.loads(json.dumps(tweet_data._json))
            tweets.append(d)

        for t_, tweet_text in enumerate(tweets):
            hashtags = tweet_text['entities'].get("hashtags", [])
            if hashtags:
                hashtags = [h['text'] for h in tweet_text['entities'].get("hashtags", [])]

            tweet_dict = {
                "name": tweet_text['user'].get('name', user_id),
                "mined_at": int(time.time()),
                "created_at": tweet_text['created_at'],
                "text": tweet_text['full_text'],
                "hashtags": hashtags,
                "source": tweet_text['source']
            }
            data_to_insert.append(InsertOne(tweet_dict))

        mongo['user_timeline_data'].bulk_write(data_to_insert)
        return True

    def get_tweets_from_hashtag(self, hashtag: list, count: int, agg_type: str):
        try:
            place = self.api.geo_search(query="India", granularity="country")
            place_id = place[0].id
            data_to_insert = []

            for tweet in tweepy.Cursor(self.api.search, q=f"place:{place_id} {f' {agg_type} '.join(hashtag)}", tweet_mode='extended').items(count):
                hashtag_tweet_dict = {
                    "mined_at": int(time.time()),
                    "text": tweet.full_text,
                    "created_at": tweet.created_at,
                    "user_location": tweet.user.location,
                    "category": hashtag,
                    "agg_by": agg_type
                }
                data_to_insert.append(InsertOne(hashtag_tweet_dict))

            mongo['hashtag_specific_data'].bulk_write(data_to_insert)
            return True
        except Exception as e:
            print(str(e))
            pass


if __name__ == "__main__":
    t = TwitterHandler()
    from config import TRACKED_USERS

    # for u in tqdm(TRACKED_USERS):
    #     t.get_user_timeline(user_id=u, count=50)

    # print(t.get_user_timeline(user_id="@covid19indiaorg", count=20))
    #
    for _ in tqdm(range(10)):
        x = random.choice(['#Help', '#Help', '#Urgent', '#urgent', "#Available", "#available"])
        y = random.choice(["#Beds", "#Oxygen", "#Remdesivir", "#Ventilator", "#Vaccine"])

        t.get_tweets_from_hashtag(hashtag=[x, y], count=50, agg_type=random.choice(['AND']))

    # print(t.get_tweets_from_hashtag(hashtag=["#Beds", "#Urgent", "#Help", "#Oxygen", "#Remdesivir", "#Ventilator"], count=200, agg_type="OR"))