
import requests
import sqlite3
import os

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# DATABASE
DATABASE = os.path.join(os.path.dirname(__file__), "students.db")

# PARTNER API
PARTNER_API_URL = "https://pacardoapriljoy-1.onrender.com/api/students"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================
# CREATE DATABASE TABLE
# =====================================

def create_table():
    conn = get_db_connection()

    conn.execute("""
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
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    ]

    if "source" not in columns:
        conn.execute("""
            ALTER TABLE students
            ADD COLUMN source TEXT DEFAULT 'Local'
        """)

    conn.execute("""
        UPDATE students
        SET source = 'Local'
        WHERE source IS NULL OR source = ''
    """)

    conn.commit()
    conn.close()


# Initialize database for Flask and Gunicorn
create_table()


# =====================================
# HOME PAGE
# =====================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================
# PREVIOUS LABORATORY API
# =====================================

@app.route("/student")
def get_student():
    return jsonify({
        "student_id": "23-0006",
        "name": "Francine Escultura",
        "program": "BSIT",
        "year": 3,
        "section": "3B"
    })


@app.route("/hello")
def hello():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/hobbies")
def hobbies():
    return jsonify({
        "name": "Francine",
        "hobbies": [
            "Listening to music",
            "Watching movies",
            "Learning programming"
        ],
        "total": 3
    })


@app.route("/studyhours")
def studyhours():
    hours = request.args.get("hours")

    if hours is None:
        return jsonify({"error": "Please provide study hours"}), 400

    try:
        hours = float(hours)
    except ValueError:
        return jsonify({"error": "Invalid study hours"}), 400

    if hours < 0 or hours > 24:
        return jsonify({
            "error": "Hours must be between 0 and 24"
        }), 400

    return jsonify({
        "study_hours": hours,
        "message": f"You studied for {hours} hours."
    })


# =====================================
# GET ALL STUDENTS
# =====================================

@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# =====================================
# ADD STUDENT
# =====================================

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    source = data.get("source", "External API")

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            source
        ))

        conn.commit()

        return jsonify({
            "message": "Student added successfully!",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# GET ONE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# =====================================
# UPDATE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            UPDATE students
            SET student_id=?, name=?, program=?, year=?, section=?
            WHERE id=?
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            id
        ))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({
            "message": "Student updated successfully!"
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Student ID already exists"
        }), 409

    finally:
        conn.close()


# =====================================
# DELETE STUDENT
# =====================================

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "message": "Student deleted successfully!"
    })


# =====================================
# RETRIEVE PARTNER RECORDS
# =====================================

@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        response = requests.get(
            PARTNER_API_URL,
            timeout=30
        )

        response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            return jsonify({
                "error": "Partner API did not return a list"
            }), 502

        return jsonify(records)

    except requests.RequestException:
        return jsonify({
            "error": "Unable to retrieve partner data. Check the partner API URL."
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner returned invalid JSON"
        }), 502


# =====================================
# IMPORT PARTNER RECORD
# =====================================

@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["student_id"],
            data["name"],
            data["program"],
            year,
            data["section"],
            "Classmate API"
        ))

        conn.commit()

        return jsonify({
            "message": "Remote record saved successfully!",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This Student ID already exists in your database."
        }), 409

    finally:
        conn.close()


# =====================================
# SEND RECORD TO PARTNER
# =====================================

@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = [
        "student_id", "name", "program", "year", "section"
    ]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        record = {
            "student_id": data["student_id"],
            "name": data["name"],
            "program": data["program"],
            "year": int(data["year"]),
            "section": data["section"],
            "source": "Partner API"
        }

        response = requests.post(
            PARTNER_API_URL,
            json=record,
            timeout=15
        )

        try:
            partner_result = response.json()
        except ValueError:
            partner_result = response.text

        return jsonify({
            "message": "Partner API response",
            "status_code": response.status_code,
            "response": partner_result
        }), 200 if response.ok else 502

    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    except requests.RequestException as error:
        return jsonify({
            "error": "Unable to send record",
            "details": str(error)
        }), 502


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == '__main__':
    app.run(debug=True, port=5002)
