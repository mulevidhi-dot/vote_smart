from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            message TEXT NOT NULL,
            rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age_group TEXT,
            registration_awareness TEXT,
            voting_awareness TEXT,
            official_source_awareness TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER,
            total INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/voter-guide")
def voter_guide():
    return render_template("voter_guide.html")


@app.route("/rights")
def rights():
    return render_template("rights.html")


@app.route("/misinformation")
def misinformation():
    return render_template("misinformation.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/quiz-result", methods=["POST"])
def quiz_result():

    name = request.form.get("name", "Anonymous")

    questions = [
        "q1",
        "q2",
        "q3",
        "q4",
        "q5"
    ]

    correct_answers = {
        "q1": "b",
        "q2": "a",
        "q3": "c",
        "q4": "b",
        "q5": "a"
    }

    score = 0

    for question in questions:
        answer = request.form.get(question)

        if answer == correct_answers[question]:
            score += 1

    conn = get_db()

    conn.execute(
        """
        INSERT INTO quiz_results
        (name, score, total)
        VALUES (?, ?, ?)
        """,
        (name, score, len(questions))
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        name=name,
        score=score,
        total=len(questions)
    )


@app.route("/survey", methods=["GET", "POST"])
def survey():

    if request.method == "POST":

        age_group = request.form.get("age_group")
        registration_awareness = request.form.get(
            "registration_awareness"
        )
        voting_awareness = request.form.get(
            "voting_awareness"
        )
        official_source_awareness = request.form.get(
            "official_source_awareness"
        )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO survey
            (
                age_group,
                registration_awareness,
                voting_awareness,
                official_source_awareness
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                age_group,
                registration_awareness,
                voting_awareness,
                official_source_awareness
            )
        )

        conn.commit()
        conn.close()

        return render_template("survey.html", submitted=True)

    return render_template("survey.html", submitted=False)


@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        rating = request.form.get("rating")

        conn = get_db()

        conn.execute(
            """
            INSERT INTO feedback
            (name, email, message, rating)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, message, rating)
        )

        conn.commit()
        conn.close()

        return render_template("feedback.html", submitted=True)

    return render_template("feedback.html", submitted=False)


@app.route("/admin")
def admin():

    conn = get_db()

    feedback_count = conn.execute(
        "SELECT COUNT(*) FROM feedback"
    ).fetchone()[0]

    survey_count = conn.execute(
        "SELECT COUNT(*) FROM survey"
    ).fetchone()[0]

    quiz_count = conn.execute(
        "SELECT COUNT(*) FROM quiz_results"
    ).fetchone()[0]

    results = conn.execute(
        """
        SELECT * FROM quiz_results
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        feedback_count=feedback_count,
        survey_count=survey_count,
        quiz_count=quiz_count,
        results=results
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)