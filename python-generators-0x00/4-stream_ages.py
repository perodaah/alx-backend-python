import mysql.connector
from mysql.connector import Error
from typing import Generator
from seed import DatabaseManager

def stream_user_ages() -> Generator[int, None, None]:
    """
    Generator that yields user ages one by one from the database.
    
    Yields:
        Integer representing user age
    """
    db_manager = None
    cursor = None
    
    try:
        # Create DatabaseManager instance and connect to ALX_prodev
        db_manager = DatabaseManager()
        connection = db_manager.connect_to_prodev()
        
        # Create a server-side cursor for efficient memory usage
        cursor = connection.cursor()
        
        # Execute query to get only ages
        cursor.execute("SELECT age FROM user_data")
        
        # LOOP 1: Stream ages one by one
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # Yield just the age value
            
    except Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if db_manager:
            db_manager.close_connection()

def calculate_average_age() -> float:
    """
    Calculates the average age of all users using the generator.
    Processes ages one by one without loading entire dataset into memory.
    
    Returns:
        Float representing the average age
    """
    total_age = 0
    user_count = 0
    
    # LOOP 2: Process ages from generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1
    
    # Calculate average (handle division by zero)
    if user_count == 0:
        return 0.0
    
    average_age = total_age / user_count
    return average_age
