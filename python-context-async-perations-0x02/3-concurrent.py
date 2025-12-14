import asyncio
import aiosqlite
from datetime import datetime

# Database setup - create a sample database with users table
async def setup_database():
    """Create and populate the database with sample data"""
    async with aiosqlite.connect('users.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT
            )
        ''')
        
        # Insert sample data
        sample_users = [
            ('Alice Johnson', 28, 'alice@email.com'),
            ('Bob Smith', 35, 'bob@email.com'),
            ('Charlie Brown', 42, 'charlie@email.com'),
            ('Diana Prince', 38, 'diana@email.com'),
            ('Ethan Hunt', 45, 'ethan@email.com'),
            ('Fiona Gallagher', 52, 'fiona@email.com'),
            ('George Miller', 29, 'george@email.com'),
            ('Hannah Baker', 47, 'hannah@email.com')
        ]
        
        await db.executemany(
            'INSERT INTO users (name, age, email) VALUES (?, ?, ?)',
            sample_users
        )
        await db.commit()
        print("Database setup completed with sample data")

async def async_fetch_users():
    """Fetch all users from the database"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting to fetch all users...")
    
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users') as cursor:
            users = await cursor.fetchall()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetched {len(users)} users")
    return users

async def async_fetch_older_users():
    """Fetch users older than 40 from the database"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting to fetch users older than 40...")
    
    async with aiosqlite.connect('users.db') as db:
        async with db.execute('SELECT * FROM users WHERE age > 40') as cursor:
            older_users = await cursor.fetchall()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetched {len(older_users)} users older than 40")
    return older_users

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting concurrent database queries...")
    
    # Execute both queries concurrently
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True  # Handle exceptions gracefully
    )
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] All queries completed!")
    return results

async def main():
    """Main function to run the entire process"""
    # Setup database first
    await setup_database()
    
    # Run concurrent queries
    all_users, older_users = await fetch_concurrently()
    
    # Display results
    print("\n" + "="*50)
    print("QUERY RESULTS:")
    print("="*50)
    
    print(f"\nAll Users ({len(all_users)} total):")
    for user in all_users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")
    
    print(f"\nUsers Older Than 40 ({len(older_users)} found):")
    for user in older_users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, Email: {user[3]}")

# Alternative main function that shows the timing benefit
async def main_with_timing():
    """Main function that demonstrates the timing benefit of concurrent execution"""
    await setup_database()
    
    print("\n" + "="*60)
    print("DEMONSTRATING CONCURRENT EXECUTION TIMING")
    print("="*60)
    
    # Add artificial delay to simulate more realistic database operations
    async def async_fetch_users_with_delay():
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Starting all users query...")
        await asyncio.sleep(1)  # Simulate database processing time
        async with aiosqlite.connect('users.db') as db:
            async with db.execute('SELECT * FROM users') as cursor:
                users = await cursor.fetchall()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Completed all users query")
        return users
    
    async def async_fetch_older_users_with_delay():
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Starting older users query...")
        await asyncio.sleep(1)  # Simulate database processing time
        async with aiosqlite.connect('users.db') as db:
            async with db.execute('SELECT * FROM users WHERE age > 40') as cursor:
                older_users = await cursor.fetchall()
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] Completed older users query")
        return older_users
    
    async def fetch_concurrently_with_delay():
        print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')}] Starting CONCURRENT queries...")
        start_time = datetime.now()
        
        results = await asyncio.gather(
            async_fetch_users_with_delay(),
            async_fetch_older_users_with_delay()
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\nConcurrent execution completed in {duration:.2f} seconds")
        return results
    
    # Run the concurrent version with delays
    await fetch_concurrently_with_delay()

if __name__ == "__main__":
    # Install aiosqlite if not already installed
    try:
        import aiosqlite
    except ImportError:
        print("Please install aiosqlite: pip install aiosqlite")
        exit(1)
    
    # Run the main demonstration
    asyncio.run(main())
    
    # Uncomment the line below to see the timing demonstration
    # asyncio.run(main_with_timing())