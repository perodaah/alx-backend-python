import sqlite3
import logging
from datetime import datetime
#### decorator to lof SQL queries




def log_queries(func):
    def log_wrapper(*args, **kwargs):
        print(f"QUERY: {kwargs['query']}")
        func(*args, **kwargs)

    return log_wrapper

def log_query_duration(func):
    def log_wrapper(*args, **kwargs):
        start = datetime.now()
        func(*args, **kwargs)
        print(f"Query Duration: {(datetime.now() - start).total_seconds() * 1000 }ms")


    return log_wrapper


@log_query_duration
@log_queries
def create_users_table(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### Create user table befor testing with fetch_all_users
users_table = create_users_table(query="""CREATE TABLE IF NOT EXISTS "User" (
    user_id UUID PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    phone_number VARCHAR,
    role user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")
users = fetch_all_users(query="SELECT * FROM User")








