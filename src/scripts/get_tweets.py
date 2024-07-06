import random
import time
import uuid
from datetime import datetime
import traceback
import sys

import os
print("Current working directory:", os.getcwd())

sys.path.append('/Users/bibbycodes/code/tweety_scraper/src/')

from src.db.pg import get_cursor_and_conn, parse_string_to_number
from src.db.utils import expand_and_parse_tweets, user_to_dict
from src.tests import get_repos
from src.utils import get_app, get_mentions_data, get_symbols_data

cursor, conn = get_cursor_and_conn()
repos = get_repos(cursor, conn)


def get_tweets_cron():
    app = get_app()
    user_repo = repos['users']
    tweet_repo = repos['tweets']
    mentions_repo = repos['mentions']
    symbols_repo = repos['symbols']

    users = user_repo.get_users_not_updated_in_last_24_hours(['username', 'twitter_id'])

    print(users)
    user = random.choice(users)
    user_repo.create_user_if_not_exists(user)

    print(user)

    username, twitter_id = user
    twitter_id = int(twitter_id)
    print(f"Fetching user: {username}")
    twitter_user = app.get_user_info(username=username)
    print(twitter_user)
    sleep_duration = random.uniform(0, 5)
    print(f'Sleeping for {sleep_duration} seconds')
    time.sleep(sleep_duration)

    print(f"Fetching tweets for {username}")
    time.sleep(sleep_duration)
    all_tweets = app.get_tweets(twitter_user.username, replies=True)
    inserted_tweets = tweet_repo.get_tweets(['tweet_id'])
    tweet_ids = [str(tweet[0]) for tweet in inserted_tweets]
    parsed_tweets = expand_and_parse_tweets(all_tweets)
    print(len(parsed_tweets))
    tweets_to_insert = [tweet for tweet in parsed_tweets if str(tweet['tweet_id']) not in tweet_ids]
    print(len(tweets_to_insert))

    # if len(tweets_to_insert) > 0 and tweets_to_insert[0]['twitter_user_id'] is not twitter_id:
    #     user_repo.update_user_twitter_id(tweets_to_insert[0]['twitter_user_id'], user[2])

    for tweet in tweets_to_insert:
        tweet['date'] = datetime.fromtimestamp(tweet['date'])
        tweet['views'] = parse_string_to_number(tweet['views'])
        tweet['created_on'] = datetime.fromtimestamp(tweet['created_on'])
        mentions_data = get_mentions_data(tweet)
        symbols_data = get_symbols_data(tweet)
        try:
            if tweet['twitter_user_id'] == twitter_id:
                tweet_repo.insert_tweet_data(tweet)
            for symbol_data in symbols_data:
                symbols_repo.insert_symbol_data(symbol_data)
            for mention_data in mentions_data:
                mentions_repo.insert_mention_data(mention_data)
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            conn.rollback()
            continue

    parsed_user = user_to_dict(twitter_user)
    parsed_user['last_fetched'] = datetime.fromtimestamp(datetime.now().timestamp())
    user_repo.update_user(twitter_id, parsed_user)
    conn.commit()

    print('Tweets inserted successfully.')
    return [tweet['text'] for tweet in tweets_to_insert]


while True:
    try:
        get_tweets_cron()
        # random number between 45 and 60
        random.uniform(45, 60)
        time.sleep(random.uniform(30, 60))
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        random.uniform(200, 300)
        time.sleep(random.uniform(30, 60))
