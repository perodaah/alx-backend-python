import mysql.connector
from mysql.connector import Error
from typing import Generator, List, Dict, Any
from seed import DatabaseManager

def paginate_users(page_size: int, offset: int) -> List[Dict[str, Any]]:
    """
    Fetches a specific page of users from the database.
    
    Args:
        page_size: Number of users per page
        offset: Starting position for the page
    
    Returns:
        List of user dictionaries for the requested page
    """
    db_manager = None
    cursor = None
    
    try:
        # Create DatabaseManager instance and connect to ALX_prodev
        db_manager = DatabaseManager()
        connection = db_manager.connect_to_prodev()
        
        # Create a cursor
        cursor = connection.cursor(dictionary=True)
        
        # Execute paginated query
        query = """
            SELECT user_id, name, email, age 
            FROM user_data 
            ORDER BY user_id 
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (page_size, offset))
        
        # Fetch all results for this page
        users = [dict(row) for row in cursor.fetchall()]
        return users
        
    except Error as e:
        print(f"Database error in paginate_users: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if db_manager:
            db_manager.close_connection()

def lazy_paginate(page_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator that lazily loads paginated user data one page at a time.
    Only fetches the next page when needed.
    
    Args:
        page_size: Number of users per page
    
    Yields:
        List of user dictionaries for each page
    """
    offset = 0
    
    # SINGLE LOOP: Continue until no more users are returned
    while True:
        # Fetch the next page only when generator is iterated
        print(f"Fetching page with offset {offset}, page size {page_size}")
        current_page = paginate_users(page_size, offset)
        
        # If no users returned, we've reached the end
        if not current_page:
            print("✅ Reached end of data")
            break
        
        # Yield the current page
        yield current_page
        
        # Move to next page
        offset += page_size
        