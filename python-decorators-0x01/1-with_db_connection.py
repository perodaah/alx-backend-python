import sqlite3 
import functools

# decorator to automatically open and close a database connection
def with_db_connection(func):
    def wrapper(*args, **kwargs):
        # setup: open connection
        conn=sqlite3.connect("users.db")
        try:
              # call the wrapped function, passing connection as first argument
            results=func(conn, *args, **kwargs)
        finally: 
            # teardown: always close connection (even if an error occurs) 
            conn.close()
        return results
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

#### Fetch user by ID with automatic connection handling 
user = get_user_by_id(user_id=1)
print(user)

""" We shouldn’t write "return result" before "conn.close()", and here’s why, explained clearly:
Once Python reaches return result,
➡ it immediately exits the function and never executes conn.close().

So the database connection stays open — that’s called a resource leak.
If you keep running the code in a loop, we’ll eventually hit an error like: """
       
          
            
        

