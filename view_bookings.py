import sqlite3
import os

db_path = 'hotel_bookings.db'

def print_table_rows(cursor, table_name, limit):
    """Fetches and prints a limited number of rows from a table."""
    try:
        query = f"SELECT * FROM \"{table_name}\" LIMIT {limit};" # Use quotes for table names that might be keywords
        cursor.execute(query)
        rows = cursor.fetchall()

        if rows:
            column_names = [description[0] for description in cursor.description]
            print(f"\n--- First {limit} row(s) from the '{table_name}' table ---")
            print(", ".join(column_names))
            print("-" * (len(", ".join(column_names)) if column_names else 40)) # Adjust separator length
            for row in rows:
                # Convert row elements to string for printing, handle None
                print(tuple(str(item) if item is not None else 'NULL' for item in row))
        else:
            print(f"\n--- No rows found in the table '{table_name}' ---")
    except sqlite3.Error as e:
        print(f"\n--- An error occurred while querying table '{table_name}': {e} ---")


if not os.path.exists(db_path):
    print(f"Error: Database file not found at {db_path}")
else:
    conn = None # Initialize conn to None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
        else:
            print(f"Querying tables in {db_path}:")
            for table_tuple in tables:
                table_name = table_tuple[0]
                # Skip sqlite internal sequence table if desired
                if table_name == 'sqlite_sequence':
                    continue

                limit = 3 if table_name == 'bookings' else 5
                print_table_rows(cursor, table_name, limit)

    except sqlite3.Error as e:
        print(f"\nAn overall database error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()
            print("\nDatabase connection closed.")