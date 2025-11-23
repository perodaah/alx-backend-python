import asyncio
import aiosqlite 
#When you use sqlite3, every query blocks the program until it finishes.With aiosqlite, the program can run multiple queries concurrently.

async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db: 
        print("Connected to database for all users query.")
        
        """  This opens the connection asynchronously.It works like with sqlite3.connect(), but non-blocking.
    Once the with block ends, the connection is automatically closed.
    Think of it as: “Start using the database connection. When done, close it — even if an error occurs.”
 """
        # Create a cursor and execute query asynchronously
        async with db.execute("SELECT * FROM users") as cursor:
            results= await cursor.fetchall()

            """ await=> pauses execution only for this function, not the whole program.While it’s waiting for the 
            database to respond, other async tasks (like async_fetch_older_users()) can run.
 """

async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        print("Connected to database for query of older users")
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            results=await cursor.fetchall()
            print("Fetched users older than 40.")
            return results


# Define a main async function to run both queries concurrently
async def fetch_concurrently():
    all_users, older_users= await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )        
        
     # Print results from both
    print("\n=== All Users ===")
    print(all_users)

    print("\n=== Users Older Than 40 ===")
    print(older_users)


# Run the asynchronous main function
asyncio.run(fetch_concurrently())       
           
           