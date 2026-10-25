
from flask import Flask, request, redirect, render_template
import os
import sqlite3

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_PATH", "library.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)


@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    with get_db() as conn:
        if search:
            books = conn.execute(
                """
                SELECT * FROM books
                WHERE title LIKE ? OR author LIKE ?
                ORDER BY id DESC
                """,
                (f"%{search}%", f"%{search}%")
            ).fetchall()
        else:
            books = conn.execute(
                "SELECT * FROM books ORDER BY id DESC"
            ).fetchall()

    return render_template(
        "index.html",
        books=books,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()

    if not title or not author or not category:
        return "All fields are required", 400

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO books (title, author, category)
            VALUES (?, ?, ?)
            """,
            (title, author, category)
        )

    return redirect("/")


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM books WHERE id = ?",
            (book_id,)
        )

    return redirect("/")


@app.route("/health")
def health():
    return {"status": "ok"}, 200


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
