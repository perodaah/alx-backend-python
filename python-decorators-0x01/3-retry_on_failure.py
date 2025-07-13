import time
import sqlite3 
import functools

def with_db_connection(func):
    def db_wrapper(*args, **kwargs) -> sqlite3.Connection:
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs) 
            return result
        finally:
            conn.close()

    return db_wrapper

def retry_on_failure(retries=3, delay=2):  
    def decorator(func):
        @functools.wraps(func)
        def retry_wrapper(*args, **kwargs):
            retry_count = 0
            while retry_count <= retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Attempt {retry_count + 1} failed: {e}")
                    retry_count += 1
                    if retry_count > retries:
                        print("Max retries exceeded.")
                        raise
                    time.sleep(delay)
        
        return retry_wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    return cursor.fetchall()

    #### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)


