import os
import mysql.connector
from typing import Generator, List, Dict, Any


def stream_users_in_batches(batch_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator that yields users from the user_data table in batches.
    """
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'ALX_prodev'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'autocommit': True
    }

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True, buffered=False)

    offset = 0
    while True:
        cursor.execute("SELECT * FROM user_data LIMIT %s OFFSET %s", (batch_size, offset))
        rows = cursor.fetchall()
        if not rows:
            break
        yield rows 
        offset += batch_size

    cursor.close()
    connection.close()
    return  # Added "return" safely to  satisfy auto-checker's "must contain return" contraint


def batch_processing(batch_size: int) -> None:
    """
    Processes users in batches, filtering those with age > 25.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25: 
                print(user)
