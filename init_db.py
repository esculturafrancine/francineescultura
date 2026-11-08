
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")

conn = sqlite3.connect(DATABASE)

conn.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialized successfully!")
