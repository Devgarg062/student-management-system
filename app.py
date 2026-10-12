
from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)
DATABASE = "students.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL
            )
        """)


@app.route("/")
def home():
    with get_db() as conn:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", students=students)


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()

    if not name or not email or not course:
        return "All fields are required", 400

    with get_db() as conn:
        conn.execute(
            "INSERT INTO students (name, email, course) VALUES (?, ?, ?)",
            (name, email, course)
        )

    return redirect("/")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )
    return redirect("/")


@app.route("/health")
def health():
    return {"status": "ok"}, 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
