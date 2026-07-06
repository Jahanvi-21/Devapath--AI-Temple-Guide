# kitna data inseted hai  users.db database mein check karne ke liye 

import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")

rows = cursor.fetchall()

print(rows)

conn.close()


