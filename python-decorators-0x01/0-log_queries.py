import sqlite3
import functools
from datetime import datetime

#### decorator to log SQL queries

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from kwargs or args
        query = kwargs.get('query', None)
        if query is None and len(args) > 0:
            query = args[0]  # Assume query is the first positional argument
        
        # Get current timestamp
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Log the SQL query with timestamp
        print(f"[{timestamp}] Executing SQL Query: {query}")
        
        # Execute the original function
        result = func(*args, **kwargs)
        
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
