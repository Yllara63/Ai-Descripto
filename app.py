import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

DB_NAME = "users.db"

# ---------- DATABASE SETUP ----------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                credits INTEGER DEFAULT 5
            )
        """)

init_db()

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    if not email:
        return redirect("/")

    session["email"] = email
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        if not user:
            cur.execute("INSERT INTO users (email, credits) VALUES (?, ?)", (email, 5))
            conn.commit()

    return redirect("/")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- HOME ----------
@app.route("/")
def index():
    email = session.get("email")
    credits = None
    if email:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT credits FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            if row:
                credits = row[0]
    return render_template("index.html", email=email, credits=credits)

# ---------- GENERATE ----------
@app.route("/generate", methods=["POST"])
def generate():
    email = session.get("email")
    if not email:
        return redirect("/")

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT credits FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if not row or row[0] <= 0:
            return "Out of credits", 403

        cur.execute("UPDATE users SET credits = credits - 1 WHERE email = ?", (email,))
        conn.commit()

    return jsonify({"result": "Generated result here..."})

if __name__ == "__main__":
    app.run(debug=True)
