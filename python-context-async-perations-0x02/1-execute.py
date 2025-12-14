import sqlite3

class ExecuteQuery:
    '''
    Reusable context manager that takes a query as input and 
    executes it, managing both connection and the query execution
    '''
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.cursor = None

    def __enter__(self):
        # Open database connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        # Execute the query with parameters
        self.cursor.execute(self.query, self.params)
        return self.cursor  # So we can fetch results in 'with' block

    def __exit__(self, exc_type, exc_value, traceback):
        # Commit changes if no exception, else rollback
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        # Clean up resources
        self.cursor.close()
        self.connection.close()
        # Returning False means exceptions (if any) are not suppressed
        return False


# Example usage:
query = "SELECT * FROM users WHERE age > ?"
param = (25,)

with ExecuteQuery("example.db", query, param) as cursor:
    results = cursor.fetchall()
    for row in results:
        print(row)
