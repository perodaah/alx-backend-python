import sqlite3 
import functools

def with_db_connection(func):
    """ your code goes here""" 
    def db_wrapper(*args, **kwargs) -> sqlite3.Connection:
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs) 
            return result
        finally:
            conn.close()

    return db_wrapper

@with_db_connection 
def get_user_by_id(conn: sqlite3.Connection, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,)) 
    return cursor.fetchone() 
    #### Fetch user by ID with automatic connection handling 


user = get_user_by_id(user_id=1)
print(user)
