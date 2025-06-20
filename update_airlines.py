import sqlite3

carrier_map = {
    "WS": "WestJet",
    "VS": "Virgin Atlantic",
    "UA": "United Airlines",
    "TP": "TAP Air Portugal",
    "S4": "Azores Airlines",
    "RJ": "Royal Jordanian",
    "QR": "Qatar Airways",
    "NH": "All Nippon Airways",
    "JL": "Japan Airlines",
    "HA": "Hawaiian Airlines",
    "FI": "Icelandair",
    "EY": "Etihad Airways",
    "DE": "Condor",
    "CA": "Air China",
    "B6": "JetBlue Airways",
    "AS": "Alaska Airlines",
    "AI": "Air India"
}


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE flights ADD COLUMN airline_full_name TEXT;")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'airline_full_name' already exists. Skipping creation.")
    else:
        raise


cursor.execute("SELECT id, airline FROM flights;")
rows = cursor.fetchall()

# iterate through the rows and make the full airline name
for row_id, code in rows:
    full_name = carrier_map.get(code)
    if full_name:
        cursor.execute(
            "UPDATE flights SET airline_full_name = ? WHERE id = ?;",
            (full_name, row_id)
        )


conn.commit()
conn.close()

print("Airline names updated successfully.")