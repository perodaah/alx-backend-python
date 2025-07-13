from datetime import datetime
import time
import sqlite3 
import functools

query_cache = {}

def log_query_duration(func):
    def log_wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        print(f"Query Duration: {(datetime.now() - start).total_seconds() * 1000 }ms")
        return result
    return log_wrapper

def with_db_connection(func):
    @functools.wraps(func)
    def db_wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return db_wrapper

def cache_query(func):
    @functools.wraps(func)
    def cache_wrapper(*args, **kwargs):
        # Extract query string from args or kwargs
        query = kwargs.get('query')
        if not query and len(args) > 1:
            query = args[1]  # args[0] is `conn`, args[1] is likely the query

        # Check the cache
        if query in query_cache:
            print("🔁 Cache hit")
            return query_cache[query]

        print("💾 Cache miss — querying DB")
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result

    return cache_wrapper


@log_query_duration
@with_db_connection
@cache_query
def fetch_users_with_cache(conn: sqlite3.Connection, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM User")
print(users)

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM User")
print(users_again)
