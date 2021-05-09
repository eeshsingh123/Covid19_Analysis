import tweepy
from tweepy import OAuthHandler
from pymongo import InsertOne, MongoClient
import pandas as pd

from config import MONGO_URL, DB_NAME, SEARCH_BY_HASHTAG

mongo = MongoClient(MONGO_URL)[DB_NAME]


def display_collected_trending_data():
    data = list(mongo['trending_data'].find({}))
    print(data)


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


def remove_tracked_user(user_list: list):
    for user in user_list:
        db_data = mongo['user_timeline_data'].delete_many({"name": user})
        print(f"Deleted {user} data: {db_data.deleted_count}")

    return True

def de_emojify(text):
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return ""


if __name__ == "__main__":
    # get_single_user_tweets(user_id='@covid19indiaorg')
    # get_single_user_tweets(hashtag="bed")

    # col_list = ['twitter_bed_data', 'twitter_covid_data', 'twitter_oxygen_data', 'twitter_stream_data', 'twitter_ventilator_data']
    # drop_collections_mongo(['twitter_stream_data'])

    # check_mongo_collection_data('twitter_stream_data')
    # display_collected_trending_data()

    print(remove_tracked_user(["Covid India Seva"]))