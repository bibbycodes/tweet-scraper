import os
import psycopg2 as psycopg2

from src.db.pg import get_cursor_and_conn

db_params = {
    'dbname': 'crypto_twitter',
    'user': 'bibbycodes',
    'host': 'localhost',
    'port': '5432'
}

def create_db():
    try:
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_folder = os.path.join(current_script_dir, '..', 'schemas', 'sql')
        cursor, conn = get_cursor_and_conn()

        for sql_file in os.listdir(sql_folder):
            if sql_file.endswith('.sql'):
                sql_path = os.path.join(sql_folder, sql_file)
                with open(sql_path, 'r') as file:
                    sql_statement = file.read()
                    cursor.execute(sql_statement)

        conn.commit()
        print("Tables created successfully.")

    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
