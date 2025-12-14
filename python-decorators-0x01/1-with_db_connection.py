import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that automatically handles opening and closing database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open a new database connection
        conn = sqlite3.connect('database.db')  # You can modify the database path as needed
        
        try:
            # Call the original function with the connection as the first argument
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            # Re-raise any exceptions that occur
            raise e
        finally:
            # Always close the connection, whether successful or not
            conn.close()
    
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling 
user = get_user_by_id(user_id=1)
print(user)