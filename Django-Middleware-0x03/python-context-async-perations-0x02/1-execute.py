import sqlite3
class ExecuteQuery:
    def __init__(self, query, params=()):
        self.query= query
        self.params=params
        self.conn= None
        self.cursor = None
        self.results = None

    def __enter__(self):
        # Step 1: Connect to database
        self.conn=sqlite3.connect("users.db")
        self.cursor=self.conn.cursor()
        print("Database connected.")

        # Step 2: Execute the query safely
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()

        # Step 3: Return the results
        return self.results
    
    def __exit__(self,exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
            print("Cursor closed.")
        if self.conn:
            self.conn.close()
            print("Connection closed.")
        #Returning False allows Python to re-raise any exceptions
        return False
    
# Usage
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
    print("Query results:", results)
