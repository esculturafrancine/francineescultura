
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "23-0006",
        "name": "Francine Escultura",
        "program": "BSIT",
        "year": 3,
        "section": "3B"
    })

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({"message": f"Hello, {name}!"})

@app.route('/hobbies')
def get_hobbies():
    return jsonify({
        "student": "Francine Escultura",
        "hobbies": [
            "Listening to music",
            "Watching movies",
            "Learning programming"
        ]
    })

@app.route('/studyhours')
def study_hours():
    hours = request.args.get('hours', default=None, type=float)

    if hours is None or hours < 0 or hours > 24:
        return jsonify({"error": "Enter study hours between 0 and 24."}), 400

    return jsonify({
        "student": "Francine Escultura",
        "study_hours": hours
    })

# Get all students from the database
@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])

# Get one student by ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))

# Additional task: Get students by section
@app.route('/students/section/<section>')
def get_students_by_section(section):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE section = ?', (section,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
