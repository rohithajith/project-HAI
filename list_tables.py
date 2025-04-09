import sqlite3

db_path = 'hotel_bookings.db'

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get the names of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Tables found in the database:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("No tables found in the database.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection
    if conn:
        conn.close()