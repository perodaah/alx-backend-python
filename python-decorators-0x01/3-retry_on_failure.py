import time
import sqlite3 
import functools

#### paste your with_db_decorator here
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn=sqlite3.connect('users.db')
        try:
            results=func(conn, *args, **kwargs)
        finally:
            conn.close()
        return results
    return wrapper
""" your code goes here"""
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    # Try to execute the wrapped function
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    # sqlite3.OperationalError = typical transient DB issue
                    print(f"Attempt {attempt} failed due to: {e}")
                    if attempt == retries:
                        print("All retry attempts failed. Raising error.")
                        raise   # re-raise last error if max retries reached
                    else:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)  # wait before retry
        return wrapper
    return decorator

            

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)