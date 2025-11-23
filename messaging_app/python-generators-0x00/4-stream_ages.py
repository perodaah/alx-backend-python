#!/usr/bin/python3
seed = __import__('seed')

def stream_user_ages():
    """
    Generator that streams (yields) user ages one by one
    from the user_data table.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:  # loop 1
        yield row["age"]

    cursor.close()
    connection.close()


def calculate_average_age():
    """
    Uses the generator to calculate the average user age
    without loading all data into memory.
    """
    total_age = 0
    count = 0

    for age in stream_user_ages():  # loop 2
        total_age += age
        count += 1

    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")
    else:
        print("No user data found.")
