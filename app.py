import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
# The fallback key is for local development only; set SPENDLY_SECRET_KEY in production.
app.secret_key = os.environ.get("SPENDLY_SECRET_KEY", "dev-only-insecure-key")

# Checked when the email is unknown so both login failures do similar work.
_DUMMY_HASH = generate_password_hash("not-a-real-password")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


def _valid_email(email):
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def fail(error):
        return render_template("register.html", error=error, name=name, email=email)

    if not name or not email or not password:
        return fail("All fields are required.")
    if not _valid_email(email):
        return fail("Enter a valid email address.")
    if len(password) < 8:
        return fail("Password must be at least 8 characters.")

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return fail("An account with this email already exists.")
    finally:
        conn.close()

    return redirect(url_for("login", registered=1))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def fail():
        return render_template("login.html", error="Invalid email or password.", email=email)

    if not email or not password:
        return fail()

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    hash_to_check = user["password_hash"] if user else _DUMMY_HASH
    if not check_password_hash(hash_to_check, password) or user is None:
        return fail()

    session.clear()
    session["user_id"] = user["id"]
    session["name"] = user["name"]
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
