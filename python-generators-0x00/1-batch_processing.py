from typing import Generator, List, Dict, Any
from seed import DatabaseManager
import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator function that streams rows from user_data table in batches.

    Args:
        batch_size: Number of rows to fetch in each batch

    Yields:
        List of dictionaries containing user data batches
    """
    db_manager = None
    cursor = None

    try:
        # Create DatabaseManager instance and connect to ALX_prodev
        db_manager = DatabaseManager()
        connection = db_manager.connect_to_prodev()

        # Create a server-side cursor for efficient memory usage
        cursor = connection.cursor(dictionary=True)

        # Execute query
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        # LOOP 1: Batch streaming loop
        while True:
            rows = cursor.fetchmany(batch_size)  # Get batch of rows
            if not rows:  # No more rows
                break

            # Convert each row to dictionary and yield the batch
            batch = [dict(row) for row in rows]
            yield batch

    except Error as e:
        print(f"Database error: {e}")
        raise
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if db_manager:
            db_manager.close_connection()


def batch_processing(batch_size: int = 100) -> Generator[Dict[str, Any], None, None]:
    """
    Processes batches of users to filter those over age 25.

    Args:
        batch_size: Number of rows to process in each batch

    Yields:
        Individual user dictionaries for users over age 25
    """
    # LOOP 2: Iterate through batches from stream_users_in_batches
    for batch in stream_users_in_batches(batch_size):
        # LOOP 3: Process each user in the current batch
        for user in batch:
            if user['age'] > 25:
                yield user
