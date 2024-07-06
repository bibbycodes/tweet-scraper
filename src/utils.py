import os
import uuid

from dotenv import load_dotenv
from tweety import Twitter

from src.db.pg import get_cursor_and_conn
from src.db.repos.mentions_repository import MentionsRepository
from src.db.repos.symbols_repository import SymbolsRepository
from src.db.repos.tweets_repository import TweetsRepository
from src.db.repos.users_repository import UserRepository

load_dotenv()

def get_repos(cursor, conn):
    users_repo = UserRepository(cursor, conn)
    tweets_repo = TweetsRepository(cursor, conn)
    mentions_repo = MentionsRepository(cursor, conn)
    symbols_repo = SymbolsRepository(cursor, conn)
    return {
        'users': users_repo,
        'tweets': tweets_repo,
        'mentions': mentions_repo,
        'symbols': symbols_repo
    }


def get_app():
    rand_string = str(uuid.uuid4())
    app = Twitter(rand_string)
    username = get_env_var('username')
    password = get_env_var('password')
    app.sign_in(username=username, password=password)
    return app

def get_app_with_creds(username, password):
    rand_string = str(f"{username}_session")
    app = Twitter(rand_string)
    app.start(username=username, password=password)
    return app

def is_dev():
    environment = os.environ.get('env')
    return environment == 'dev'


def get_db_uri():
    return os.environ.get('mongo_uri') if not is_dev() else 'mongodb://localhost:27017/cryptotweets'


def to_dict(obj):
    if isinstance(obj, list):
        return [to_dict(e) for e in obj]
    elif hasattr(obj, "__dict__"):
        return {k: to_dict(v) for k, v in obj.__dict__.items()}
    else:
        return obj


def get_env_variables():
    env_vars = [
        "user_name", "password", "email",
        "mongodb_user_name", "mongodb_password", "mongo_uri", "env"
    ]

    extracted_vars = {var: os.environ.get(var) for var in env_vars}
    return extracted_vars


def get_env_var(var):
    return os.environ.get(var)


def is_thread(thread_or_tweet):
    if hasattr(thread_or_tweet, 'tweets'):
        return True
    return False


def get_mentions_data(tweet):
    mentions = tweet['user_mentions']

    return [{
        'tweet_id': tweet['tweet_id'],
        'twitter_user_id': tweet['twitter_user_id'],
        'username_mentioned': mention['username'],
        'twitter_user_id_mentioned': mention['twitter_user_id']
    } for mention in mentions]


def get_symbols_data(tweet):
    symbols = tweet['symbols']
    return [
        {
            'tweet_id': tweet['tweet_id'],
            'twitter_user_id': tweet['twitter_user_id'],
            'symbol': symbol
        } for symbol in symbols
    ]

def get_apps():
    username_a = get_env_var('username_a')
    password_a = get_env_var('password_a')
    app_a = get_app_with_creds(username_a, password_a)
    username_b = get_env_var('username_b')
    password_b = get_env_var('password_b')
    app_b = get_app_with_creds(username_b, password_b)
    return app_a, app_b
