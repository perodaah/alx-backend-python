from seed import connect_to_prodev


def stream_user_ages():
    """
    Generator that yields user ages one by one from the database
    """
    connection = connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")
    for (age,) in cursor:
        yield age
    cursor.close()
    connection.close()


def average_user_age():
    """
    Computes average age using the stream, without loading all rows
    """
    total = 0
    count = 0
    for age in stream_user_ages():
        total += age     
        count += 1
    if count == 0:
        return 0
    return total / count 
