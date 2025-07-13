# Python Generators: Streaming and Batching with MySQL

This project demonstrates the use of Python generators to efficiently stream and process data from a MySQL database without loading the entire dataset into memory.

## Files

- **seed.py**  
  Sets up the MySQL database (`ALX_prodev`), creates the `user_data` table, and inserts data from `user_data.csv`.

- **0-stream_users.py**  
  Streams user records one by one using a generator and optional row limit.

- **1-batch_processing.py**  
  Streams user data in batches and filters users with `age > 25` using a generator.

- **2-lazy_paginate.py**  
  Implements lazy pagination by fetching pages only when needed using a generator with offset.

- **4-stream_ages.py**  
  Streams user ages using a generator and calculates the average age without using SQL `AVG()`.

## Notes

- All database connections are made using environment variables for configuration.
- Generator functions are used to reduce memory usage and simulate real-world data streaming.
