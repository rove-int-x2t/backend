import sqlite3
import csv

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM flights')
rows = cursor.fetchall()

column_names = [description[0] for description in cursor.description]

with open('flights.csv','w', newline='',encoding='utf8') as f:
    writer = csv.writer(f)
    writer.writerow(column_names) # this is like the first row which is the name of the columns 
    writer.writerows(rows)

print("Exported flights to a csv file successfully")
conn.close()
