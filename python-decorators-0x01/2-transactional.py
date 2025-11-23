import sqlite3 
import functools

"""your code goes here"""
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
          
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn,*args, **kwargs):
       try:
          result = func(conn, *args, **kwargs)  # execute SQL commands
          conn.commit()                         # commit changes if successful
       except Exception as e:
          conn.rollback()                       # rollback if any error occurs
          print(f"❌ Transaction rolled back due to error: {e}")
          raise                                  # re-raise error so it's visible
       return result
    return wrapper
       
@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
 cursor = conn.cursor() 
 cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')

"""that ensures a function running a database operation is wrapped inside a 
transaction.
If the function raises an error, rollback; otherwise commit the transaction. """