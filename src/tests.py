import json
import random
import time
from datetime import datetime

import psycopg2

from src.db.db import DatabaseHandler
from src.db.pg import get_cursor_and_conn, parse_string_to_number
from src.db.utils import expand_and_parse_tweets, user_to_dict
from src.utils import get_app, get_repos, get_mentions_data, get_symbols_data

curser, conn = get_cursor_and_conn()


def get_tweets_for_user():
    app = get_app()
    user = app.get_user_info(username='milesdeutscher')
    all_tweets = app.get_tweets(user.username, replies=True)
    return expand_and_parse_tweets(all_tweets)


def get_users():
    app = get_app()
    db = DatabaseHandler()
    already_saved_users = db.get_users()
    already_saved_user_handles = [f"@{user['username']}" for user in already_saved_users]

    with open('memefluencers.json', 'r') as json_file:
        data = json.load(json_file)
        random.shuffle(data)
        data = [username for username in data if username not in already_saved_user_handles]
        for username in data:
            user_handle = username.split('@')[1]
            twitter_user = app.get_user_info(username=user_handle)
            user = user_to_dict(twitter_user)
            sleep_duration = random.uniform(0, 20)
            time.sleep(sleep_duration)
            result = db.insert_user(user)
            if result:
                print(f'inserted user {user_handle}')
            else:
                print(f'user already exists {user_handle}')


def add_new_users(input_file_with_usernames, category):
    cursor, conn = get_cursor_and_conn()
    app = get_app()
    user_repo = get_repos(cursor, conn)['users']
    already_saved_users = user_repo.get_users()
    already_saved_user_handles = [f"@{user['username']}" for user in already_saved_users]

    with open(input_file_with_usernames, 'r') as json_file:
        data = json.load(json_file)
        random.shuffle(data)
        data = [username for username in data if username not in already_saved_user_handles]
        for username in data:
            user_handle = username.split('@')[1]
            twitter_user = app.get_user_info(username=user_handle)
            user = user_to_dict(twitter_user)

            if (user['username'] not in already_saved_user_handles):
                user['categories'] = [category]
            else:
                user['categories'].append(category)
            sleep_duration = random.uniform(0, 20)
            time.sleep(sleep_duration)
            result = user_repo.insert_user(user)
            if result:
                print(f'inserted user {user_handle}')
            else:
                print(f'user already exists {user_handle}')


def copy_users_to_pg():
    vcs = []
    influencers = []
    memefluencers = []
    db = DatabaseHandler()
    cursor, conn = get_cursor_and_conn()
    user_repo = get_repos(cursor, conn)['users']
    pg_users = user_repo.get_all_users(['username'])
    users_mongo = list(db.get_users())
    with open('influencers.json', 'r') as json_file:
        data = json.load(json_file)
        for handle in data:
            user_handle = handle.split('@')[1]
            influencers.append(user_handle)

    with open('vcs.json', 'r') as json_file:
        data = json.load(json_file)
        for handle in data:
            user_handle = handle.split('@')[1]
            vcs.append(user_handle)

    with open('memefluencers.json', 'r') as json_file:
        data = json.load(json_file)
        for handle in data:
            user_handle = handle.split('@')[1]
            memefluencers.append(user_handle)

    pg_user_names = [user[0] for user in pg_users]
    users_not_in_pg = []

    for user in users_mongo:
        print(user['username'])
        if user['username'] not in pg_user_names:
            users_not_in_pg.append(user)

    print(len(users_not_in_pg), len(pg_user_names))
    for user in users_not_in_pg:
        handle = user['username']
        category = ''
        if handle in vcs:
            category = 'VC'

        if handle in influencers:
            category = 'INFLUENCER'

        if handle in memefluencers:
            category = 'MEME_INFLUENCER'

        user['categories'] = [category]
        user['twitter_created_at'] = datetime.fromtimestamp(user['created_at'])
        user['date'] = datetime.fromtimestamp(user['date'])
        del user['created_at']
        user_repo.insert_user_data(user)

    conn.commit()


def insert_tweets_pg():
    repos = get_repos()
    tweet_repo = repos['tweets']
    mentions_repo = repos['mentions']
    symbols_repo = repos['symbols']
    inserted_tweets = tweet_repo.get_tweets(['tweet_id'])
    tweet_ids = [str(tweet[0]) for tweet in inserted_tweets]
    with open('../tweets.json') as json_file:
        data = json.load(json_file)
        for tweet in data:
            if str(tweet['tweet_id']) not in tweet_ids:
                tweet['date'] = datetime.fromtimestamp(tweet['date'])
                tweet['views'] = parse_string_to_number(tweet['views'])
                tweet['created_on'] = datetime.fromtimestamp(tweet['created_on'])
                tweet_repo.insert_tweet_data(tweet)
                mentions_data = get_mentions_data(tweet)
                symbols_data = get_symbols_data(tweet)
                for symbol_data in symbols_data:
                    symbols_repo.insert_symbol_data(symbol_data)
                for mention_data in mentions_data:
                    mentions_repo.insert_mention_data(mention_data)
    conn.commit()


def drop_all_tables():
    try:
        cursor, conn = get_cursor_and_conn()

        table_names = [
            'users',
            'tweets',
            'symbols',
            'mentions'
        ]

        for table_name in table_names:
            drop_table_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
            cursor.execute(drop_table_query)
            conn.commit()
            print(f"Table '{table_name}' dropped successfully.")

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error dropping tables: {e}")


# 
# 
# drop_all_tables()
# create_db()
# copy_users_to_pg()
# insert_tweets_pg()
# add_new_users('memefluencers.json', 'MEME_INFLUENCER')
