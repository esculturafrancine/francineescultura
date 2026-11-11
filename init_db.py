
import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
""")

columns = [
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(students)"
    ).fetchall()
]

if "source" not in columns:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN source TEXT DEFAULT 'Local'
    """)

cursor.execute("""
    UPDATE students
    SET source = 'Local'
    WHERE source IS NULL OR source = ''
""")

conn.commit()
conn.close()

print("Database initialized successfully!")
