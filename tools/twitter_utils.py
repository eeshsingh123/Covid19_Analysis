import time

import tweepy
from tweepy import OAuthHandler
from pymongo import InsertOne, MongoClient
import pandas as pd

from creds.credentials import CONSUMER_KEY, CONSUMER_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from config import MONGO_URL, DB_NAME, SEARCH_BY_HASHTAG

mongo = MongoClient(MONGO_URL)[DB_NAME]


def get_single_user_tweets(user_id=None, hashtag=None, print_test=False, count=150):
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if user_id and not hashtag:
        data_to_insert = []

        tweets = api.user_timeline(
            screen_name=user_id,
            include_rts=False,
            tweet_mode='extended',
            exclude_replies=True,
            count=count
        )

        for t_, tweet_text in enumerate(tweets):
            if print_test:
                print(f"ID -> {tweet_text.id}")
                print(f"created_at -> {tweet_text.created_at}")
                print(f"text-> {tweet_text.full_text}")
                print("="*50)

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

        mongo['user_specific_data'].bulk_write(data_to_insert)
        return True

    elif hashtag:
        place = api.geo_search(query="India", granularity="country")
        place_id = place[0].id
        hashtag_data_to_insert = []

        for tweet in tweepy.Cursor(api.search, q=f"place:{place_id} #{SEARCH_BY_HASHTAG[hashtag]}").items(count):
            if print_test:
                print(tweet.text)
                print(tweet.created_at)
                print("=========================================")

            hashtag_tweet_dict = {
                "mined_at": int(time.time()),
                "text": tweet.text,
                "created_at": tweet.created_at
            }
            hashtag_data_to_insert.append(InsertOne(hashtag_tweet_dict))

        mongo['hashtag_specific_data'].bulk_write(hashtag_data_to_insert)
        return True


def drop_collections_mongo(collections_list):
    for col in collections_list:
        deleted_c = mongo[col].delete_many({})
        mongo[col].drop()
        print(deleted_c.deleted_count)


def check_mongo_collection_data(collection_name):
    # db_data = list(mongo[collection_name].find({"category": {"$nin": ["General"]}}))
    df = pd.DataFrame(list(mongo['twitter_stream_data'].aggregate([
        {"$sort": {"timestamp_ms": -1}},
        {"$limit": 2000},
        {"$match": {"category": {"$nin": ["General"]}}}])))
    df.to_csv("C:\\Users\\eeshs\\Desktop\\test.csv")
    return df


def de_emojify(text):
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return ""


if __name__ == "__main__":
    # get_single_user_tweets(user_id='@covid19indiaorg')
    # get_single_user_tweets(hashtag="bed")

    # col_list = ['twitter_bed_data', 'twitter_covid_data', 'twitter_oxygen_data', 'twitter_stream_data', 'twitter_ventilator_data']
    drop_collections_mongo(['twitter_stream_data'])

    # check_mongo_collection_data('twitter_stream_data')
