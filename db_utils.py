import sqlite3

def init_db(db_path="database.db"):
    """
    Initializes the SQLite database and creates the flights table if it doesn't exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS flights")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT,
            departure TEXT,
            arrival TEXT,
            date TEXT,
            price TEXT,
            airline TEXT,
            flight_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def append_flight_data(flight_data, db_path="database.db"):
    """
    Appends a list of flight data dictionaries to the SQLite database,
    using the provided departure and arrival locations.
    """
    if not flight_data:
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for flight in flight_data:
        cursor.execute("""
            INSERT INTO flights (flight_number, departure, arrival, date, price, airline, flight_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            flight.get("flight_number"),
            flight.get("departure"),
            flight.get("arrival"),
            flight.get("date"),
            flight.get("price"),
            flight.get("airline"),
            flight.get("flight_time"),
        ))
    conn.commit()
    conn.close()