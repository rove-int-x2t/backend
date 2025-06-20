import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('SELECT DISTINCT airline from flights;')
distinct_airlines = cursor.fetchall()

for airline in distinct_airlines:
    print(airline[0])
    
conn.close()
