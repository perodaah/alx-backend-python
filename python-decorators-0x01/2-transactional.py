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

def transactional(func):
    """Decorator that automatically handles database transactions (commit/rollback)"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function within a transaction
            result = func(conn, *args, **kwargs)
            # If no exception was raised, commit the transaction
            conn.commit()
            return result
        except Exception as e:
            # If an exception occurred, rollback the transaction
            conn.rollback()
            # Re-raise the exception to notify the caller
            raise e
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')