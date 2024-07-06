from datetime import datetime, timedelta
import json

import psycopg2
import psycopg2.extras

from src.db.pg import get_fields_string
from src.db.repos.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def update_user_twitter_id(self, twitter_id, id):
        try:
            update_query = """
                UPDATE users
                SET twitter_id = %s
                WHERE id = %s
            """
            self.cursor.execute(update_query, (twitter_id, id))
            self.connection.commit()
            print("User twitter id updated successfully.")
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def create_user_if_not_exists(self, user_data):
        user = self.get_user_by_twitter_id(user_data[1], ['twitter_id'])
        if user is None:
            self.insert_user_data(user_data)
        else:
            print("User already exists.")

    def insert_user_data(self, user_data):
        try:
            insert_query = """
                INSERT INTO users (
                    twitter_id,
                    rest_id,
                    twitter_created_at,
                    date,
                    description,
                    bio,
                    entities,
                    fast_followers_count,
                    favourites_count,
                    followers_count,
                    friends_count,
                    listed_count,
                    location,
                    media_count,
                    name,
                    normal_followers_count,
                    profile_banner_url,
                    profile_image_url_https,
                    protected,
                    screen_name,
                    username,
                    statuses_count,
                    verified,
                    pinned_tweets,
                    community_role,
                    categories
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """
            data = (
                user_data['twitter_id'],
                user_data['rest_id'],
                user_data['twitter_created_at'],
                user_data['date'],
                user_data['description'],
                user_data['bio'],
                psycopg2.extras.Json(user_data['entities']),
                user_data['fast_followers_count'],
                user_data['favourites_count'],
                user_data['followers_count'],
                user_data['friends_count'],
                user_data['listed_count'],
                user_data['location'],
                user_data['media_count'],
                user_data['name'],
                user_data['normal_followers_count'],
                user_data['profile_banner_url'],
                user_data['profile_image_url_https'],
                user_data['protected'],
                user_data['screen_name'],
                user_data['username'],
                user_data['statuses_count'],
                user_data['verified'],
                user_data['pinned_tweets'],
                user_data['community_role'],
                user_data['categories']
            )

            sql_statement = self.cursor.mogrify(insert_query, data).decode('utf-8')
            print(sql_statement)
            self.cursor.execute(insert_query, data)
            self.connection.commit()

            print("User data inserted successfully.")

        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_all_users(self, fields):
        try:
            query = f"SELECT {get_fields_string(fields)} FROM users"
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            return users
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_users_by_category(self, category, fields):
        try:
            query = f"SELECT {get_fields_string(fields)} FROM users WHERE '{category}' = ANY(categories)"
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            return users
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_user_by_twitter_id(self, twitter_id, fields):
        try:
            query = f"SELECT {get_fields_string(fields)} FROM users WHERE twitter_id = %s"
            self.cursor.execute(query, (twitter_id,))
            user = self.cursor.fetchone()
            return user
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def update_user(self, twitter_id, parsed_user):
        # Convert the 'entities' dictionary to a JSON string
        json_entities = json.dumps(parsed_user.get('entities', {}))

        update_query = """
            UPDATE users
            SET
                twitter_id = %s,
                rest_id = %s,
                created_at = %s,
                date = %s,
                description = %s,
                bio = %s,
                entities = %s,
                fast_followers_count = %s,
                favourites_count = %s,
                followers_count = %s,
                friends_count = %s,
                listed_count = %s,
                location = %s,
                media_count = %s,
                name = %s,
                normal_followers_count = %s,
                profile_banner_url = %s,
                profile_image_url_https = %s,
                protected = %s,
                screen_name = %s,
                username = %s,
                statuses_count = %s,
                verified = %s,
                pinned_tweets = %s,
                community_role = %s,
                last_fetched = %s
            WHERE twitter_id = %s
        """

        # Now, pass the JSON string as a parameter value to the execute method
        values = (
            parsed_user['twitter_id'],
            parsed_user['rest_id'],
            datetime.fromtimestamp(parsed_user['created_at']),
            datetime.fromtimestamp(parsed_user['date']),
            parsed_user['description'],
            parsed_user['bio'],
            json_entities,
            parsed_user['fast_followers_count'],
            parsed_user['favourites_count'],
            parsed_user['followers_count'],
            parsed_user['friends_count'],
            parsed_user['listed_count'],
            parsed_user['location'],
            parsed_user['media_count'],
            parsed_user['name'],
            parsed_user['normal_followers_count'],
            parsed_user['profile_banner_url'],
            parsed_user['profile_image_url_https'],
            parsed_user['protected'],
            parsed_user['screen_name'],
            parsed_user['username'],
            parsed_user['statuses_count'],
            parsed_user['verified'],
            parsed_user['pinned_tweets'],
            parsed_user['community_role'],
            parsed_user['last_fetched'],
            parsed_user['twitter_id']  # Assuming twitter_id is the primary key for the WHERE clause
        )

        self.cursor.execute(update_query, values)

    def update_user_values(self, twitter_id, values):
        try:
            update_query = f"""
                UPDATE users
                SET {', '.join([f"{field} = %s" for field in values.keys()])}
                WHERE twitter_id = %s
            """
            self.cursor.execute(update_query, list(values.values()) + [twitter_id])
            self.connection.commit()
            print("User updated successfully.")
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_users_not_updated_in_last_24_hours(self, fields):
        try:
            fields_to_select = get_fields_string(fields)
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=8)
            # AND 'INFLUENCER' = ANY(categories);
            query = """
                SELECT {fields_to_select} 
                FROM users 
                WHERE (last_fetched < %s OR last_fetched IS NULL)
                """.format(fields_to_select=fields_to_select)
            self.cursor.execute(query, (twenty_four_hours_ago,))
            result = self.cursor.fetchall()

            return result

        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e

    def get_users_not_updated_in_the_last_n_minutes(self, fields, minutes):
        try:
            fields_to_select = get_fields_string(fields)
            n_minutes_ago = datetime.utcnow() - timedelta(minutes=minutes)
            query = f"""
                SELECT {fields_to_select}
                FROM users
                WHERE (last_fetched < %s OR last_fetched IS NULL)
            """
            self.cursor.execute(query, (n_minutes_ago,))
            result = self.cursor.fetchall()
            return result
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise e
