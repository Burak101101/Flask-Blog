import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")

with open('scheme.sql', 'r') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post'))
cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post'))

# Create a default user
cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('password'),"admin@gmail.com"))

connection.commit()
connection.close()
