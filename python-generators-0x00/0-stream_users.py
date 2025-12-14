from typing import Generator, Dict, Any
from seed import DatabaseManager  # Import the DatabaseManager from seed.py
import mysql.connector
from mysql.connector import Error

def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that streams rows from user_data table one by one
    using yield. Only contains one loop.
    Uses DatabaseManager from seed.py to handle database connections.
    
    Yields:
        Dictionary containing user data (user_id, name, email, age)
    """
    db_manager = None
    cursor = None
    
    try:
        # Create DatabaseManager instance and connect to ALX_prodev
        db_manager = DatabaseManager()
        connection = db_manager.connect_to_prodev()  # Use the class method
        
        # Create a server-side cursor for efficient memory usage
        cursor = connection.cursor(dictionary=True)
        
        # Execute query
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        # Single loop that yields rows one by one
        while True:
            row = cursor.fetchone()  # Get one row at a time
            if row is None:  # No more rows
                break
            yield dict(row)  # Yield the row as a dictionary
            
    except Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if db_manager:
            db_manager.close_connection()  # Use the class's cleanup method
