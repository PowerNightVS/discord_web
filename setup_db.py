import sqlite3

db = sqlite3.connect("database.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT,
    command_count INTEGER DEFAULT 0
)
""")

db.commit()
db.close()

print("Database created successfully!")
