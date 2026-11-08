
from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")


# DATABASE CONNECTION
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# PREVIOUS LABORATORY API ENDPOINTS
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
        return jsonify({"error": "Hours must be between 0 and 24"}), 400

    return jsonify({
        "study_hours": hours,
        "message": f"You studied for {hours} hours."
    })


# READ ALL STUDENTS
@app.route("/api/students", methods=["GET"])
def api_students():
    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# CREATE STUDENT
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["student_id"],
                data["name"],
                data["program"],
                year,
                data["section"]
            )
        )

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully!",
            "id": new_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    finally:
        conn.close()


# READ ONE STUDENT
@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# UPDATE STUDENT
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    required = ["student_id", "name", "program", "year", "section"]

    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return jsonify({"error": "Year must be a number"}), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT id FROM students WHERE id = ?", (id,)
    ).fetchone()

    if existing is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    try:
        conn.execute(
            """
            UPDATE students
            SET student_id=?, name=?, program=?, year=?, section=?
            WHERE id=?
            """,
            (
                data["student_id"],
                data["name"],
                data["program"],
                year,
                data["section"],
                id
            )
        )

        conn.commit()

        return jsonify({"message": "Student updated successfully!"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409

    finally:
        conn.close()


# DELETE STUDENT
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

    return jsonify({"message": "Student deleted successfully!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
