
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# Home Page - Display HTML Interface
@app.route('/')
def home():
    return render_template('index.html')


# 1. Student Information API
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "23-0006",
        "name": "Francine Escultura",
        "program": "BSIT",
        "year": 3,
        "section": "3B"
    })


# 2. Greeting API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({
        "message": f"Hello, {name}!"
    })


# 3. Hobbies API
@app.route('/hobbies')
def get_hobbies():
    return jsonify({
        "student": "Francine Escultura",
        "hobbies": [
            "Listening to music",
            "Watching movies",
            "Learning programming"
        ],
        "total_hobbies": 3
    })


# 4. Study Hours API
@app.route('/studyhours')
def study_hours():
    hours = request.args.get('hours', default=None, type=float)

    # Validate study hours
    if hours is None or hours < 0 or hours > 24:
        return jsonify({
            "error": "Please enter study hours between 0 and 24."
        }), 400

    # Provide feedback based on study hours
    if hours >= 6:
        message = "Great study effort!"
    elif hours >= 3:
        message = "Good study schedule!"
    else:
        message = "Consider spending more time studying."

    return jsonify({
        "student": "Francine Escultura",
        "study_hours": hours,
        "feedback": message
    })


# Run Flask Application
if __name__ == '__main__':
    app.run(debug=True)
