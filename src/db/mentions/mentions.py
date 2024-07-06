import psycopg2
from psycopg2.extras import Json, execute_batch

class Mention:
    def __init__(self, db_config):
        """
        Initialize with the database configuration.
        """
        self.conn = psycopg2.connect(**db_config)

    def insert_mention(self, pool_id, social_channel_id, text, raw_data, created_at, follower_count, symbol, urls, handles, token_addresses):
        """
        Insert a new record into the Mentions table.
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO "Mentions" (pool_id, social_channel_id, text, raw_data, created_at, follower_count, symbol, urls, handles, token_addresses)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_tuple = (pool_id, social_channel_id, text, Json(raw_data), created_at, follower_count, symbol, Json(urls), Json(handles), Json(token_addresses))
                cur.execute(query, data_tuple)
                self.conn.commit()
                print("Mention inserted successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"An error occurred: {e}")

    def insert_many(self, mentions):
        """
        Insert multiple mentions into the database.
        """
        query = """
        INSERT INTO "Mentions" (pool_id, social_channel_id, text, raw_data, created_at, follower_count, symbol, urls, handles, token_addresses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = [
            (m['pool_id'], m['social_channel_id'], m['text'], Json(m['raw_data']), m['created_at'], m['follower_count'], m['symbol'], Json(m['urls']), Json(m['handles']), Json(m['token_addresses']))
            for m in mentions
        ]
        try:
            with self.conn.cursor() as cur:
                execute_batch(cur, query, data, page_size=100)
                self.conn.commit()
                print(f"{len(data)} mentions inserted successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"An error occurred during batch insert: {e}")

    def find_by_text(self, search_text):
        """
        Find mentions by text.
        """
        query = 'SELECT * FROM "Mentions" WHERE text LIKE %s'
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, ('%' + search_text + '%',))
                results = cur.fetchall()
                return results
        except Exception as e:
            print(f"An error occurred while searching: {e}")
            return []

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

    def find_all(self, limit=100):
        """
        Retrieve all records from Mentions table with an optional limit on the number of records returned.
        """
        query = query = 'SELECT * FROM "Mentions" LIMIT %s'
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (limit,))
                results = cur.fetchall()
                return results
        except Exception as e:
            print(f"An error occurred while retrieving all mentions: {e}")
            return []

    def list_tables(self):
        """
        List all tables in the database.
        """
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                tables = [table[0] for table in cur.fetchall()]
                return tables
        except psycopg2.Error as e:
            print(f"Error fetching tables: {e}")
            return []

def get_mentions_db():
    db_config = {
        'dbname': 'degen_galore',
        'user': 'bibbycodes',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432'
    }

    return Mention(db_config)
