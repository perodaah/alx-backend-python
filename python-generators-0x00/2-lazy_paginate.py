#!/usr/bin/python3
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetch a single page of users starting from the given offset.
    Returns a list of rows.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily fetches paginated user data from the database.
    Fetches the next page only when needed.
    Uses only one loop and yield.
    """
    offset = 0
    while True:  # only one loop allowed
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size  # move to next page
