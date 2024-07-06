import psycopg2

from src.db.pg import get_fields_string
from src.db.repos.base_repository import BaseRepository


class SymbolsRepository(BaseRepository):
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def insert_symbol_data(self, tweet):
        try:
            insert_query = """
                INSERT INTO symbols (symbol, tweet_id, twitter_user_id) VALUES (%s, %s, %s) RETURNING symbol_id
            """
            data = (
                tweet['symbol'],
                tweet['tweet_id'],
                tweet['twitter_user_id']
            )
            self.cursor.execute(insert_query, data)
            symbol_id = self.cursor.fetchone()[0]
            return symbol_id

        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_all_symbols(self, fields):
        try:
            select_query = f"SELECT {get_fields_string(fields)} FROM symbols"
            self.cursor.execute(select_query)
            symbols = self.cursor.fetchall()
            return symbols

        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e
