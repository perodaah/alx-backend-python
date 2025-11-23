import sqlite3
from datetime import datetime 
import functools

#### decorator to log SQL queries
def log_queries(func):
    def wrapper(query):
        now = datetime.now()
        print(f"[{now}] Executing SQL query: {query}")
        result = func(query)
        return result
    return wrapper
""" YOUR CODE GOES HERE"""

@log_queries
def fetch_all_users(query):
    conn=sqlite3.connect('users.db')
    cursor=conn.cursor()
    cursor.execute(query)
    results=cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
print(users)
  

        
     
    