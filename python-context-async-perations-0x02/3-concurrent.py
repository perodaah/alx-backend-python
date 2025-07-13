import aiosqlite
import asyncio

DB_NAME = "users.db"

async def async_fetch_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM User") as cursor:
            users = await cursor.fetchall()
            print("All Users:", users)
            return users

async def async_fetch_older_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM User WHERE age > 40") as cursor:
            older_users = await cursor.fetchall()
            print("Users older than 40:", older_users)
            return older_users

async def fetch_concurrently():
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Run async functions concurrently
asyncio.run(fetch_concurrently())
