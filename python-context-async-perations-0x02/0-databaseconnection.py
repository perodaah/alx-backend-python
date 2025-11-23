import sqlite3
class DatabaseConnection:
    def __init__(self, db_name):
        # The __init__ method runs automatically when creating the object
        # It stores the database name but does not connect yet
        self.db_name = db_name
        self.conn = None   # placeholder for the connection object
        print(f"DatabaseConnection object created for {self.db_name}")


    def __enter__(self):
        self.conn=sqlite3.connect(self.db_name)
        print("Database connection opened.")
        # Return the connection so it can be used inside the 'with' block
        return self.conn


    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            print(f"Database connection to '{self.db_name}' closed.")
        # Return False so any exceptions are not suppressed
        return False


with DatabaseConnection("users.db") as conn:
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM users")
    results=cursor.fetchall
    print("Query results:", results)
