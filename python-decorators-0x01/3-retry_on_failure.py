import time
import sqlite3 
import functools
from contextlib import contextmanager

# Database connection decorator
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # If connection is already provided, use it
        if args and isinstance(args[0], sqlite3.Connection):
            return func(*args, **kwargs)
        
        # Otherwise create a new connection
        conn = sqlite3.connect('example.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper

# Retry decorator for transient errors
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                    last_exception = e
                    # Check if it's a transient error worth retrying
                    transient_errors = [
                        'database is locked',
                        'database schema has changed',
                        'unable to open database file',
                        'disk I/O error'
                    ]
                    
                    error_str = str(e).lower()
                    is_transient = any(transient_error in error_str for transient_error in transient_errors)
                    
                    if attempt < retries and is_transient:
                        print(f"Transient error encountered: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                        time.sleep(delay)
                    else:
                        # If not transient or out of retries, re-raise
                        raise last_exception
                except Exception as e:
                    # For non-transient errors, don't retry
                    raise e
            
            # This should never be reached, but just in case
            raise last_exception
        return wrapper
    return decorator