#!/usr/bin/python3
import mysql.connector
from mysql.connector import errorcode
import csv
import uuid

# ---------- 1. Connect to MySQL server (no database yet) ----------
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",         # Change if using a different MySQL user
            password="your_password"  # <-- replace with your actual password
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# ---------- 2. Create the ALX_prodev database if not exists ----------
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")

# ---------- 3. Connect directly to ALX_prodev ----------
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",  # <-- replace with your password
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# ---------- 4. Create user_data table ----------
def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(5,0) NOT NULL,
            INDEX (user_id)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")

# ---------- 5. Insert data from CSV ----------
def insert_data(connection, csv_file):
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']

                # Avoid duplicate email entries
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                if cursor.fetchone():
                    continue  # Skip if email already exists

                insert_query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, name, email, age))
        connection.commit()
        print("Data inserted successfully")
        cursor.close()
    except Exception as err:
        print(f"Error inserting data: {err}")
