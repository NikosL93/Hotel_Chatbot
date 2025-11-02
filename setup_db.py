
import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('hotel.db')
cursor = conn.cursor()

# Create hotel_rooms table
cursor.execute("""
CREATE TABLE IF NOT EXISTS hotel_rooms (
    room_id INTEGER PRIMARY KEY,
    room_type TEXT NOT NULL,
    price_per_night REAL NOT NULL,
    availability INTEGER NOT NULL
)
""")

# Create bookings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY,
    room_id INTEGER,
    guest_name TEXT NOT NULL,
    check_in_date TEXT NOT NULL,
    check_out_date TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES hotel_rooms (room_id)
)
""")

# Insert some sample data into hotel_rooms
rooms_data = [
    (101, 'Standard', 100.00, 1),
    (102, 'Standard', 100.00, 0),
    (201, 'Deluxe', 150.00, 1),
    (202, 'Deluxe', 150.00, 0),
    (301, 'Suite', 250.00, 0)
]

cursor.executemany("INSERT INTO hotel_rooms VALUES (?, ?, ?, ?)", rooms_data)

# Insert some sample data into bookings
bookings_data = [
    (1, 202, "Ioannis Papadopoulos", '2025-10-01', '2025-10-05'),
    (2, 301, "Jane Smith", '2025-11-12', '2025-11-15'),
    (3, 102, "Peter Jones", '2025-12-20', '2025-12-23')
]

cursor.executemany("INSERT INTO bookings VALUES (?, ?, ?, ?, ?)", bookings_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'hotel.db' created successfully with tables 'hotel_rooms' and 'bookings', and populated with sample data.")
