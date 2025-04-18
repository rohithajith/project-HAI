import sqlite3

# Connect to the database
conn = sqlite3.connect('hotel_bookings.db')
cursor = conn.cursor()

# Fetch all records from guest_profiles
cursor.execute("SELECT * FROM bookings;")
rows = cursor.fetchall()

# Get column names
column_names = [description[0] for description in cursor.description]

# Print results
print("Guest Profiles:\n")
for row in rows:
    profile = dict(zip(column_names, row))
    for key, value in profile.items():
        print(f"{key}: {value}")
    print("-" * 30)

# Close the connection
conn.close()