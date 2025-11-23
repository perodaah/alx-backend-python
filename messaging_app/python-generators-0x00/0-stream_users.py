#!/usr/bin/python3
import mysql.connector

def stream_users():
    """
    Generator function that streams rows from the 'user_data' table one by one.
    Uses a single loop and yields each row as a dictionary.
    """
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # <-- replace with your MySQL username
        password="yourpassword",  # <-- replace with your MySQL password
        database="your_database"  # <-- replace with your database name
    )

    cursor = conn.cursor(dictionary=True)

    # Execute query to select all rows
    cursor.execute("SELECT * FROM user_data")

    # Loop through results and yield each row one by one
    for row in cursor:
        yield row

    # Close resources
    cursor.close()
    conn.close()
