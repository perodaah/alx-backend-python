import time
import sqlite3 
import functools


query_cache = {}    # Global cache dictionary

"""your code goes here"""
def with_db_connection(func):
    """Decorator that caches database query results based on SQL string."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn= sqlite3.connect("users.db")
        try:
            results=func(conn,*args, **kwargs)
        finally:
            conn.close()
        return results
    return wrapper

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, query,*args, **kwargs):
        if query in cache_query:
            print(f"[CACHE HIT] Returning cached result for query: {query}")
            return query_cache[query]
        # Otherwise, run the actual database query
        print(f"[CACHE MISS] Executing query: {query}")
        result = func(conn, query, *args, **kwargs)
         # Store result in cache for future reuse
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")