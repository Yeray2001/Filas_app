from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

DATABASE = 'database.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuadrantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT,
            hora TEXT,
            filas_1 TEXT,
            filas_2 TEXT,
            filas_3 TEXT,
            filas_4 TEXT
        )
        """)
        cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, is_admin)
        VALUES ('admin', ?, 1)
        """, (generate_password_hash("1234"),))
        conn.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['is_admin'] = user[3]
            return redirect('/cuadrante')
        else:
            return "Usuario o contraseña incorrectos", 403

@app.route('/cuadrante')
def cuadrante():
    if 'user_id' not in session:
        return redirect('/')
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuadrantes")
        cuadrantes = cursor.fetchall()
    return render_template('cuadrante.html', cuadrantes=cuadrantes)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
