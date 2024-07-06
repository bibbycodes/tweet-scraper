import psycopg2


def get_cursor_and_conn():
    db_params = {
        'dbname': 'crypto_twitter',
        'user': 'bibbycodes',
        'host': 'localhost',
        'port': '5432'
    }

    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    return cursor, conn


def get_fields_string(fields):
    return ', '.join(fields) if (fields is not None) or (fields is not []) else '*'

def parse_string_to_number(s):
    try:
        return int(s)  # Try parsing as an integer
    except ValueError:
        try:
            return float(s)  # Try parsing as a float
        except ValueError:
            return 0 
