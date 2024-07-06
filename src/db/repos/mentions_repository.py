import psycopg2

class MentionsRepository:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def insert_mention_data(self, mentions_data):
        try:
            insert_query = """
                INSERT INTO mentions (
                    tweet_id,
                    twitter_user_id,
                    twitter_user_id_mentioned,
                    username_mentioned
                ) VALUES (
                    %s, %s, %s, %s
                )
            """
            data = (
                mentions_data['tweet_id'],
                mentions_data['twitter_user_id'],
                mentions_data['twitter_user_id_mentioned'],
                mentions_data['username_mentioned']
            )
            self.cursor.execute(insert_query, data)
            print("Mention data inserted successfully.")
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"Error inserting mention data: {e}")
            raise e
