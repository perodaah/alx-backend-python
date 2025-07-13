import sqlite3

class Sqlite3DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor  # What gets assigned to `as` in the with block

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                print(f"Error occurred: {exc_val}")
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()



with Sqlite3DatabaseConnection('users.db') as cursor:
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(results)



