import time
import sqlite3 
import functools

query_cache = {}

def cache_query(func):
    """Decorator that caches the results of database queries based on the SQL query string."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from kwargs
        query = kwargs.get('query')
        
        # If no query found in kwargs, try to find it in args
        if query is None and len(args) > 1:
            # Assuming query is the second argument (after conn)
            query = args[1]
        
        if query is None:
            # If no query parameter found, execute without caching
            return func(*args, **kwargs)
        
        # Check if query result is already cached
        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
        
        # Execute the query and cache the result
        print(f"Executing query and caching result: {query}")
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    
    return wrapper

def with_db_connection(func):
    """Decorator to handle database connection."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # For demonstration, create an in-memory SQLite database
        conn = sqlite3.connect(':memory:')
        try:
            # Create a sample users table for testing
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT
                )
            ''')
            # Insert some sample data
            cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES ('Alice', 'alice@example.com')")
            cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES ('Bob', 'bob@example.com')")
            conn.commit()
            
            # Call the original function with the connection
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Test the implementation
if __name__ == "__main__":
    # First call will cache the result
    print("=== First call ===")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Users: {users}")
    
    # Second call will use the cached result
    print("\n=== Second call ===")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(f"Users again: {users_again}")
    
    # Different query will execute fresh
    print("\n=== Different query ===")
    specific_user = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice'")
    print(f"Specific user: {specific_user}")
    