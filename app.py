

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Francine Escultura - My API</title>
        </head>
        <body>
            <h1>Welcome to Francine Escultura's API!</h1>
            <p>BSIT - 3rd Year - Section 3B</p>
            <p>Student ID: 23-0006</p>
            <h2>Available API Endpoints</h2>
            <ul>
                <li><a href="/student">Student Information</a></li>
                <li><a href="/hello?name=Francine">Hello API</a></li>
                <li><a href="/hobbies">My Hobbies</a></li>
                <li><a href="/studyhours?hours=4">Study Hours API</a></li>
            </ul>
        </body>
    </html>
    """


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
    return jsonify({
        "message": f"Hello, {name}!"
    })


# New Endpoint 1: Personal hobbies
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


# New Endpoint 2: Study hours calculator
@app.route('/studyhours')
def study_hours():
    hours = request.args.get('hours', default=None, type=float)

    if hours is None or hours < 0 or hours > 24:
        return jsonify({
            "error": "Please enter study hours between 0 and 24."
        }), 400

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


if __name__ == '__main__':
    app.run(debug=True)