
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Clear old records before adding the five sample records
cursor.execute("DELETE FROM students")

students = [
    ('23-0006', 'Francine Escultura', 'BSIT', 3, '3B'),
    ('23-0007', 'Ruby joy molina', 'BSIT', 3, '3A'),
    ('24-0008', 'Missy meranda', 'BSIT', 2, '2A'),
    ('24-0009', 'Hapee malones', 'BSIT', 2, '2B'),
    ('25-0010', 'April joy molina', 'BSIT', 1, '1A')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
