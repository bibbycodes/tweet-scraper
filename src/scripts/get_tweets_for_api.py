import random
import random
import sys
import time
import traceback
from datetime import datetime, timedelta

from src.api.dgen_galore import DgenGlore
from src.lib.app_manager import AppManager

sys.path.append('/Users/bibbycodes/code/tweety_scraper/src/')

from src.db.pg import get_cursor_and_conn, parse_string_to_number
from src.db.utils import expand_and_parse_tweets, tweet_to_dict_for_api
from src.tests import get_repos
from src.utils import get_mentions_data, get_symbols_data

cursor, conn = get_cursor_and_conn()
repos = get_repos(cursor, conn)


def update_users():
    user_repo = repos['users']
    users = user_repo.get_all_users(['username', 'last_fetched', 'twitter_id'])
    usernames = []

    with open('influencers.json', 'r') as file:
        influencers = json.load(file)
        for influencer in influencers:
            usernames.append({"username": influencer, "category": "INFLUENCER"})

    with open('memefluencers.json', 'r') as file:
        memefluencers = json.load(file)
        for memefluencer in memefluencers:
            usernames.append({"username": memefluencer, "category": "MEME_INFLUENCER"})

    with open('vcs.json', 'r') as file:
        crypto_influencers = json.load(file)
        for crypto_influencer in crypto_influencers:
            usernames.append({"username": crypto_influencer, "category": "VC"})

    usernames_not_in_db = [user['username'] for user in usernames if user['username'] not in [u[0] for u in users]]
    print(f"Users not in the database: {usernames_not_in_db}")

def get_tweets_for_api_cron(app):
    user_repo = repos['users']
    tweet_repo = repos['tweets']
    mentions_repo = repos['mentions']
    symbols_repo = repos['symbols']

    users = user_repo.get_users_by_category('MEME_INFLUENCER', ['username', 'last_fetched', 'twitter_id'])
    memefluencers_not_updated_in_last_10_minutes = [user for user in users if
                                                    user[1] is None or user[1] < datetime.now() - timedelta(minutes=10)]

    user = random.choice(memefluencers_not_updated_in_last_10_minutes)

    username, last_fetched, twitter_id = user
    twitter_user_id = int(twitter_id)
    twitter_user = app.get_user_info(username=username)
    print(f"Fetching tweets for {username}")
    sleep_duration = random.uniform(0, 5)
    time.sleep(sleep_duration)
    all_tweets = app.get_tweets(username, replies=True)
    parsed_tweets = expand_and_parse_tweets(all_tweets)
    print(f"Found {len(parsed_tweets)} tweets for {username}")
    tweet_ids = [tweet['tweet_id'] for tweet in parsed_tweets if tweet and 'tweet_id' in tweet], ['tweet_id']
    if len(tweet_ids) == 0:
        inserted_tweets = tweet_repo.get_tweets_by_ids(tweet_ids)
    else:
        inserted_tweets = []
    print(f"Found {len(inserted_tweets)} tweets already in the database.")
    tweet_ids = [str(tweet[0]) for tweet in inserted_tweets]
    tweets_to_insert = [tweet for tweet in parsed_tweets if str(tweet['tweet_id']) not in tweet_ids]
    print(f"Found {len(tweets_to_insert)} new tweets to insert.")

    api_parsed_tweets = [tweet_to_dict_for_api(tweet, twitter_user) for tweet in parsed_tweets if
                         str(tweet['tweet_id']) not in tweet_ids]

    for tweet in tweets_to_insert:
        tweet['date'] = datetime.fromtimestamp(tweet['date'])
        tweet['views'] = parse_string_to_number(tweet['views'])
        tweet['created_on'] = datetime.fromtimestamp(tweet['created_on'])
        mentions_data = get_mentions_data(tweet)
        symbols_data = get_symbols_data(tweet)
        try:
            if tweet['twitter_user_id'] == twitter_user_id:
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

    dgen_api = DgenGlore("http://localhost:4000")
    for tweet in api_parsed_tweets:
        tweet['date'] = tweet['created_at'] * 1000
        tweet['created_at'] = tweet['created_at'] * 1000

    unique_mentioned_symbols = list(set(symbol for tweet in api_parsed_tweets for symbol in tweet['symbols']))
    print(f"Symbols mentioned: {unique_mentioned_symbols}")
    try:
        print(f"Posting {len(api_parsed_tweets)} tweets to DGen API")
        dgen_api.post_mentions({"mentions": api_parsed_tweets})
    except Exception as e:
        print(f"Error occurred posting tweets: {e}")
        traceback.print_exc()
        conn.rollback()

    user_repo.update_user_values(twitter_id, {'last_fetched': datetime.fromtimestamp(datetime.now().timestamp())})
    conn.commit()

    print('Tweets inserted successfully.')
    return [tweet['text'] for tweet in tweets_to_insert]


app_manager = AppManager()

while True:
    try:
        app = app_manager.get_next()
        get_tweets_for_api_cron(app)
        time.sleep(random.uniform(30, 45))
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        random.uniform(200, 300)
        time.sleep(random.uniform(200, 300))
