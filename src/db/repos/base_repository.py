import psycopg2


class BaseRepository:
    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def commit(self):
        try:
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"Error during commit: {e}")
