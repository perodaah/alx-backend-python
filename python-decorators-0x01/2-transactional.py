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

def transactional(func):
    @functools.wraps(func)
    def transaction_wrapper(conn: sqlite3.Connection, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"commited conn {result}")
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed and rolled back: {e}")
            raise
    return transaction_wrapper


@with_db_connection 
@transactional 
def update_user_email(conn: sqlite3.Connection, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE User SET email = ? WHERE user_id = ?", (new_email, user_id)) 
    return cursor.rowcount
    #### Update user's email with automatic transaction handling 

update_user_email(user_id='d290f1ee-6c54-4b01-90e6-d701748f0851', new_email='Crawford_Cartwright@hotmail.com')
