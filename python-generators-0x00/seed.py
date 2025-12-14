import mysql.connector
from mysql.connector import Error
import uuid
import csv
from typing import Generator, Dict, Any, Optional

class DatabaseManager:
    def __init__(self):
        self.connection = None
    
    def connect_db(self) -> mysql.connector.connection.MySQLConnection:
        """
        Connects to the MySQL database server
        """
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',  # Change as per your setup
                password=''   # Change as per your setup
            )
            if connection.is_connected():
                print("Connected to MySQL server")
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            raise
    
    def create_database(self, connection: mysql.connector.connection.MySQLConnection) -> None:
        """
        Creates the database ALX_prodev if it does not exist
        """
        try:
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
            print("Database ALX_prodev created or already exists")
        except Error as e:
            print(f"Error creating database: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def connect_to_prodev(self) -> mysql.connector.connection.MySQLConnection:
        """
        Connects to the ALX_prodev database in MySQL
        """
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',      # Change as per your setup
                password='',      # Change as per your setup
                database='ALX_prodev'
            )
            if connection.is_connected():
                print("Connected to ALX_prodev database")
                self.connection = connection
                return connection
        except Error as e:
            print(f"Error while connecting to ALX_prodev database: {e}")
            raise
    
    def create_table(self, connection: mysql.connector.connection.MySQLConnection) -> None:
        """
        Creates a table user_data if it does not exist with the required fields
        """
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(3,0) NOT NULL,
                INDEX idx_user_id (user_id)
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table user_data created or already exists")
        except Error as e:
            print(f"Error creating table: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def insert_data(self, connection: mysql.connector.connection.MySQLConnection, data: Dict[str, Any]) -> None:
        """
        Inserts data in the database if it does not exist
        """
        try:
            cursor = connection.cursor()
            
            # Check if user already exists
            check_query = "SELECT user_id FROM user_data WHERE user_id = %s"
            cursor.execute(check_query, (data['user_id'],))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                insert_query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    data['user_id'],
                    data['name'],
                    data['email'],
                    data['age']
                ))
                connection.commit()
                print(f"Inserted user: {data['name']}")
            else:
                print(f"User {data['name']} already exists")
                
        except Error as e:
            print(f"Error inserting data: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def load_data_from_csv(self, connection: mysql.connector.connection.MySQLConnection, csv_file_path: str) -> None:
        """
        Loads data from CSV file into the database
        """
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                
                for row in csv_reader:
                    # Generate UUID if not present in CSV
                    user_id = row.get('user_id') or str(uuid.uuid4())
                    
                    data = {
                        'user_id': user_id,
                        'name': row['name'],
                        'email': row['email'],
                        'age': int(row['age'])
                    }
                    
                    self.insert_data(connection, data)
                    
            print("Data loading from CSV completed")
            
        except FileNotFoundError:
            print(f"CSV file {csv_file_path} not found")
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            raise
    
    def stream_rows(self, connection: Optional[mysql.connector.connection.MySQLConnection] = None, 
                   batch_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Generator that streams rows from the user_data table one by one
        
        Args:
            connection: Database connection (uses self.connection if None)
            batch_size: Number of rows to fetch at a time
        
        Yields:
            Dictionary containing row data
        """
        conn = connection or self.connection
        if not conn:
            raise ValueError("No database connection provided")
        
        cursor = None
        try:
            # Use server-side cursor for efficient memory usage
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT user_id, name, email, age FROM user_data"
            cursor.execute(query)
            
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                
                for row in rows:
                    yield dict(row)
                    
        except Error as e:
            print(f"Error streaming rows: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def close_connection(self) -> None:
        """
        Closes the database connection
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")


# Example usage and demonstration
def main():
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Step 1: Connect to MySQL server and create database
        server_connection = db_manager.connect_db()
        db_manager.create_database(server_connection)
        server_connection.close()
        
        # Step 2: Connect to ALX_prodev database and create table
        prodev_connection = db_manager.connect_to_prodev()
        db_manager.create_table(prodev_connection)
        
        # Step 3: Load sample data from CSV (uncomment when you have the CSV file)
        # db_manager.load_data_from_csv(prodev_connection, 'user_data.csv')
        
        # Step 4: Insert some sample data for demonstration
        sample_data = [
            {
                'user_id': str(uuid.uuid4()),
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'age': 30
            },
            {
                'user_id': str(uuid.uuid4()),
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'age': 25
            },
            {
                'user_id': str(uuid.uuid4()),
                'name': 'Bob Johnson',
                'email': 'bob.johnson@example.com',
                'age': 35
            }
        ]
        
        for data in sample_data:
            db_manager.insert_data(prodev_connection, data)
        
        # Step 5: Demonstrate streaming rows
        print("\nStreaming rows from database:")
        for i, row in enumerate(db_manager.stream_rows(prodev_connection)):
            print(f"Row {i + 1}: {row}")
            
            # Simulate processing (you can add your business logic here)
            # For demonstration, stop after 10 rows
            if i >= 9:  # Adjust as needed
                break
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db_manager.close_connection()
