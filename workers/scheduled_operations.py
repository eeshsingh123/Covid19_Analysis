import random

from tqdm import tqdm

from workers.twitter_operations import TwitterHandler
from tools.request_handler import internal_request
from config import FLASK_PORT, TRACKED_USERS, HASHTAG_1, HASHTAG_2


def update_reports_and_twitter_endpoints():
    twit = TwitterHandler()

    for user in tqdm(TRACKED_USERS):
        twit.get_user_timeline(user_id=user, count=50)

    for _ in tqdm(range(10)):
        x = random.choice(HASHTAG_1)
        y = random.choice(HASHTAG_2)
        twit.get_tweets_from_hashtag(hashtag=[x, y], count=50, agg_type=random.choice(['AND']))

    print("Updated Twitter data -> (user, hashtag)")

    result, status = internal_request(
        port=FLASK_PORT,
        method='update_reports',
        data={}
    )
    print(result)
    return True


if __name__ == "__main__":
    print(update_reports_and_twitter_endpoints())
