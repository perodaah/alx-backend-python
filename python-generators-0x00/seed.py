import os
import mysql.connector
import csv
import uuid


def connect_db():
    """Connects to the MySQL server (no specific database)"""
    try:
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'your_database'),
            'user': os.getenv('DB_USER', 'your_username'),
            'password': os.getenv('DB_PASSWORD', 'your_password'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    """Creates ALX_prodev database if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Database creation failed: {err}")


def connect_to_prodev():
    """Connects to the ALX_prodev database"""
    try:
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'your_database'),
            'user': os.getenv('DB_USER', 'your_username'),
            'password': os.getenv('DB_PASSWORD', 'your_password'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        print(f"Connection to ALX_prodev failed: {err}")
        return None


def create_table(connection):
    """Creates user_data table if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(5, 2) NOT NULL,
                INDEX(user_id)
            );
        """)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Table creation failed: {err}")


def insert_data(connection, csv_file):
    """Inserts data into the user_data table from a CSV file"""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = float(row['age'])

                # Check if email already exists
                cursor.execute("SELECT email FROM user_data WHERE email = %s", (email,))
                if cursor.fetchone():
                    continue

                cursor.execute("""
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, age))
            connection.commit()
        cursor.close()
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found.")
    except mysql.connector.Error as err:
        print(f"Insertion error: {err}")
