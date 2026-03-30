import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, g, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mysecretkey")
DATABASE = "database.db"
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Routes ---


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            flash("Username already exists ❌", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, name, email, phone_number) VALUES (?, ?, ?, ?, ?)",
            (username, hashed_password, name, email, phone),
        )
        db.commit()

        flash("Registration successful! Please login. 🎉", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["display_name"] = user["name"] if user["name"] else user["username"]
            session["profile_pic"] = user["profile_pic"]
            flash(f"Welcome back, {session['display_name']}! 👋", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password ❌", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id=? ORDER BY created_at DESC",
        (session["user_id"],),
    )
    tasks = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()

    return render_template("dashboard.html", tasks=tasks, user=user)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        new_name = request.form.get("name")
        new_email = request.form.get("email")
        new_phone = request.form.get("phone")
        new_username = request.form.get("username")
        new_password = request.form.get("password")
        file = request.files.get("profile_pic")

        if new_username and new_username != session["username"]:
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND id != ?",
                (new_username, session["user_id"]),
            )
            if cursor.fetchone():
                flash("Username already taken! ❌", "error")
            else:
                cursor.execute(
                    "UPDATE users SET username=? WHERE id=?",
                    (new_username, session["user_id"]),
                )
                session["username"] = new_username
                db.commit()

        cursor.execute(
            "UPDATE users SET name=?, email=?, phone_number=? WHERE id=?",
            (new_name, new_email, new_phone, session["user_id"]),
        )
        session["display_name"] = new_name if new_name else session["username"]
        db.commit()

        if new_password:
            hashed_pw = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password=? WHERE id=?",
                (hashed_pw, session["user_id"]),
            )
            db.commit()

        if file and allowed_file(file.filename):
            filename = f"user_{session['user_id']}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            cursor.execute(
                "UPDATE users SET profile_pic=? WHERE id=?",
                (filename, session["user_id"]),
            )
            session["profile_pic"] = filename
            db.commit()

        flash("Profile updated successfully! ✨", "success")
        return redirect(url_for("profile"))

    cursor.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user = cursor.fetchone()
    return render_template("profile.html", user=user)


@app.route("/add_task", methods=["POST"])
def add_task():
    if "user_id" in session:
        task_text = request.form["task"]
        priority = request.form.get("priority", "Medium")
        db = get_db()
        db.execute(
            "INSERT INTO tasks (user_id, task, priority) VALUES (?, ?, ?)",
            (session["user_id"], task_text, priority),
        )
        db.commit()
        flash("Task added! 🚀", "success")
    return redirect(url_for("dashboard"))


@app.route("/edit_task/<int:id>", methods=["POST"])
def edit_task(id):
    if "user_id" in session:
        new_task = request.form.get("task")
        new_priority = request.form.get("priority")
        db = get_db()
        db.execute(
            "UPDATE tasks SET task=?, priority=? WHERE id=? AND user_id=?",
            (new_task, new_priority, id, session["user_id"]),
        )
        db.commit()
        flash("Task updated! ✨", "success")
    return redirect(url_for("dashboard"))


@app.route("/toggle/<int:id>")
def toggle_task(id):
    if "user_id" in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT status FROM tasks WHERE id=? AND user_id=?",
            (id, session["user_id"]),
        )
        task = cursor.fetchone()

        if task:
            new_status = "Completed" if task["status"] == "Pending" else "Pending"
            db.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, id))
            db.commit()
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:id>")
def delete_task(id):
    if "user_id" in session:
        db = get_db()
        db.execute(
            "DELETE FROM tasks WHERE id=? AND user_id=?", (id, session["user_id"])
        )
        db.commit()
        flash("Task removed 🗑️", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    else:
        try:
            db = sqlite3.connect(DATABASE)
            cols = [col[1] for col in db.execute("PRAGMA table_info(users)").fetchall()]
            if "name" not in cols:
                db.execute("ALTER TABLE users ADD COLUMN name TEXT")
            if "email" not in cols:
                db.execute("ALTER TABLE users ADD COLUMN email TEXT")
            if "phone_number" not in cols:
                db.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")

            task_cols = [
                col[1] for col in db.execute("PRAGMA table_info(tasks)").fetchall()
            ]
            if "priority" not in task_cols:
                db.execute(
                    "ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'"
                )

            db.commit()
            db.close()
        except Exception as e:
            print(f"Migration error: {e}")

    app.run(debug=True, port=8000)
