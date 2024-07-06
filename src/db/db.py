from dataclasses import asdict
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from ..utils import get_db_uri

ca = certifi.where()

load_dotenv()


class DatabaseHandler:
    def __init__(self):
        self.client = MongoClient(get_db_uri())
        self.db = self.client['cryptotweets']
        self.users_collection = self.db.users
        self.tweets_collection = self.db.tweets

    def insert_user(self, user):
        found_user = self.get_user_by_twitter_id(user['twitter_id'])
        if not found_user:
            return self.users_collection.insert_one(user)
        return None

    def insert_tweet(self, tweet):
        return self.tweets_collection.insert_one(tweet)

    def insert_many_tweets(self, tweets):
        """
        Insert multiple tweets into the tweets collection, handling duplicates.
        
        :param tweets: A list of tweet dictionaries to be inserted.
        :return: List of ObjectIds for the successfully inserted documents.
        """
        if not isinstance(tweets, list):
            raise ValueError("tweets should be a list of dictionaries")

        tweet_ids = [tweet["tweet_id"] for tweet in tweets]
        existing_tweets = self.get_many_by_tweet_ids(tweet_ids)
        
        existing_tweet_ids_set = set(tweet.get("tweet_id") for tweet in existing_tweets)

        # Filter out duplicate tweets before insertion
        unique_tweets = [tweet for tweet in tweets if tweet.get("tweet_id") not in existing_tweet_ids_set]

        inserted = []
        try:
            result = self.tweets_collection.insert_many(unique_tweets) if len(unique_tweets) > 0 else None
            if result:
                inserted.extend(result.inserted_ids)
        except errors.BulkWriteError as e:
            for error in e.details.get('writeErrors', []):
                if error['code'] == 11000:  # MongoDB duplicate key error code
                    # Handle the case where a tweet with the same "id" already exists
                    pass  # You can log an error or perform other actions as needed

        return inserted

    def get_many_by_tweet_ids(self, tweet_ids):
        if not isinstance(tweet_ids, list):
            raise ValueError("tweet_ids should be a list")

        existing_tweets = list(self.tweets_collection.find({"tweet_id": {"$in": tweet_ids}}))
        return existing_tweets

    def get_user(self, user_id):
        return self.users_collection.find_one({"id": user_id})

    def get_users(self):
        return self.users_collection.find({})

    def get_user_by_twitter_id(self, twitter_id):
        return self.users_collection.find_one({"twitter_id": twitter_id})
    
    def get_tweet(self, tweet_id):
        return self.tweets_collection.find_one({"id": tweet_id})

    def ping(self):
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
