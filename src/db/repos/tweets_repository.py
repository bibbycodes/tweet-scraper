import psycopg2
import psycopg2.extras

from src.db.pg import get_fields_string
from src.db.repos.base_repository import BaseRepository


class TweetsRepository(BaseRepository):
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def insert_tweet_data(self, tweet_data):
        try:
            # Define the INSERT statement for tweets
            insert_query = """
                INSERT INTO tweets (
                    tweet_id,
                    created_on,
                    date,
                    text,
                    twitter_user_id,
                    is_retweet,
                    retweeted_tweet_id,
                    is_quoted,
                    quoted_tweet_id,
                    is_reply,
                    is_sensitive,
                    reply_counts,
                    quote_counts,
                    replied_to_tweet_id,
                    bookmark_count,
                    views,
                    likes,
                    language,
                    retweet_counts,
                    source,
                    audio_space_twitter_id,
                    community_note,
                    url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
            """

            data = (
                tweet_data['tweet_id'],
                tweet_data['created_on'],
                tweet_data['date'],
                tweet_data['text'],
                tweet_data['twitter_user_id'],
                tweet_data['is_retweet'],
                tweet_data['retweeted_tweet_id'],
                tweet_data['is_quoted'],
                tweet_data['quoted_tweet_id'],
                tweet_data['is_reply'],
                tweet_data['is_sensitive'],
                tweet_data['reply_counts'],
                tweet_data['quote_counts'],
                tweet_data['replied_to_tweet_id'],
                tweet_data['bookmark_count'],
                tweet_data['views'],
                tweet_data['likes'],
                tweet_data['language'],
                tweet_data['retweet_counts'],
                tweet_data['source'],
                tweet_data['audio_space_twitter_id'],
                tweet_data['community_note'],
                tweet_data['url'],
            )
            
            self.cursor.execute(insert_query, data)

        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_tweets(self, fields):
        try:
            query = f"SELECT {get_fields_string(fields)} FROM tweets"
            self.cursor.execute(query)
            tweets = self.cursor.fetchall()
            return tweets
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_tweets_by_ids(self, tweet_ids, fields):
        try:
            query = f"SELECT  {get_fields_string(fields)}  FROM tweets WHERE tweet_id IN ({','.join(tweet_ids)})"
            self.cursor.execute(query)
            tweets = self.cursor.fetchall()
            return tweets
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e
