import sqlite3

class DatabaseConnection:
    """Context manager for SQLite database connection."""
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Enter the runtime context and return the database connection"""
        print("Opening database connection...")
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the database connection"""
        print("Closing database connection...")
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        
        # Return False to propagate any exceptions, True would suppress them
        return False

# Example usage with the context manager
def main():
    # Create a sample database and table for demonstration
    setup_sample_database()
    
    # Use the context manager with the with statement
    with DatabaseConnection('example.db') as cursor:
        # Execute the query
        cursor.execute("SELECT * FROM users")
        
        # Fetch and print the results
        results = cursor.fetchall()
        print("\nQuery Results:")
        print("ID | Name      | Email")
        print("-" * 25)
        for row in results:
            print(f"{row[0]:2} | {row[1]:9} | {row[2]}")

def setup_sample_database():
    """Create a sample database with some test data"""
    import os
    if os.path.exists('example.db'):
        os.remove('example.db')
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    
    # Insert sample data
    sample_users = [
        (1, 'Alice', 'alice@email.com'),
        (2, 'Bob', 'bob@email.com'),
        (3, 'Charlie', 'charlie@email.com'),
        (4, 'Diana', 'diana@email.com')
    ]
    
    cursor.executemany('INSERT INTO users (id, name, email) VALUES (?, ?, ?)', sample_users)
    conn.commit()
    conn.close()
    print("Sample database created successfully!")

if __name__ == "__main__":
    main()