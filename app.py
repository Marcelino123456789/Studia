import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
import time
# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure CS50 Library to use MySQL database
# Connection details come from environment variables so credentials are
# never hard-coded or committed to source control.
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError(
        "Missing database configuration. Set DB_HOST, DB_PORT, DB_USER, "
        "DB_PASSWORD, and DB_NAME environment variables."
    )

# mysql+pymysql is used (rather than plain mysql://) so the app relies on
# the pure-Python PyMySQL driver, which needs no system-level MySQL client
# libraries at deploy time.
db = SQL(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.context_processor
def inject_unread_count():
    """Make total unread message count available in every template."""

    if session.get("user_id"):

        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM messages WHERE receiver_id = ? AND is_read = 0",
            session["user_id"]
        )

        return dict(unread_count=row[0]["cnt"])

    return dict(unread_count=0)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    ##if request.method == "POST":
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get("username")
        )
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"],
            request.form.get("password")
        ):
            return apology("invalid username or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/about", methods=["GET", "POST"])
def about():
    """about"""
    if request.method == "POST":
        return redirect("/about")
    return render_template("about.html")

@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            title = request.form.get("title")
            content = request.form.get("content")
            db.execute(
                "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
                session["user_id"],
                title,
                content
            )
        elif action == "delete":
            note_id = request.form.get("note_id")
            db.execute(
                "DELETE FROM notes WHERE user_id = ? AND id = ?",
                session["user_id"],
                note_id
            )
    show = db.execute(
        "SELECT id, title, content FROM notes WHERE user_id = ?",
        session["user_id"]
    )
    return render_template("notes.html", notes=show)

@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        content = request.form.get("content")
        action = request.form.get("action")
        due_date = request.form.get("due_date")
        tasks_id = request.form.get("task_id")
        if action == "add":
            db.execute("INSERT INTO tasks (user_id,content,due_date) VALUES (?,?,?)"
                       ,session["user_id"]
                       ,content
                       ,due_date)
        elif action == "done":
            db.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?"
                       ,session["user_id"]
                       ,tasks_id)

    show = db.execute("SELECT id,content,due_date FROM tasks WHERE user_id = ? ORDER BY due_date "
                      ,session["user_id"])
    return render_template("tasks.html", tasks = show)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("must provide username")
        password = request.form.get("password")
        if not password:
            return apology("must provide password")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return apology("must provide confirmation")
        if confirmation != password:
            return apology("must be the same as password")
        try:
            hashed_password = generate_password_hash(password)
            user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hashed_password
            )
        except:
            return apology("User name is used")
        session["user_id"] = user_id
        return redirect("/")
    return render_template("register.html")


@app.route("/chat/<int:receiver_id>", methods=["GET", "POST"])
@login_required
def chat(receiver_id):
    if request.method == "POST":
        action = request.form.get("action")
        content = request.form.get("content")

        if action == "send":

            if not content:
                return apology("Please write a message")

            db.execute("INSERT INTO messages (content,sender_id,receiver_id) VALUES (?,?,?)", content, session["user_id"], receiver_id)
            db.execute("""
            DELETE FROM messages
            WHERE id IN (
            SELECT id
            FROM (
                SELECT id
                FROM messages
                WHERE (sender_id = ? AND receiver_id = ?)
                   OR (sender_id = ? AND receiver_id = ?)
                ORDER BY id DESC
                LIMIT 18446744073709551615 OFFSET 30
            ) AS old_messages
        )
        """,
        session["user_id"],
        receiver_id,
        receiver_id,
        session["user_id"]
    )

    db.execute("UPDATE messages SET is_read = 1 WHERE sender_id = ? AND receiver_id = ? AND is_read = 0"
               ,receiver_id
               ,session["user_id"])
    receiver = db.execute("SELECT username FROM users WHERE id = ?"
                          ,receiver_id)
    messages = db.execute("SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) ORDER BY id "
                          ,session["user_id"]
                          ,receiver_id
                          ,receiver_id
                          ,session["user_id"])
    return render_template("chat.html"
                           ,messages=messages
                           ,receiver_id=receiver_id
                           ,receiver_username=receiver[0]["username"])


@app.route("/search",methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        action = request.form.get("action")
        user_name_receiver = request.form.get("receiver_username")
        if action =="friends":
            friends = db.execute("SELECT friends_name FROM friends WHERE user_id = ? ORDER BY friends_name"
                                 ,session["user_id"])
            return render_template("friends.html", friends=friends)
        elif action =="search":
            if not user_name_receiver:
                return apology("Please enter a user name")
            answer = db.execute("SELECT id FROM users WHERE username = ?"
                                ,user_name_receiver)
            if not answer:
                return apology("User name not found")
            db.execute("INSERT IGNORE INTO friends (user_id,friends_name) VALUES (?,?)"
                       ,session["user_id"]
                       ,user_name_receiver)
            return redirect(url_for("chat", receiver_id=answer[0]["id"]))
    unread_messages = db.execute("SELECT users.username, COUNT(messages.id) AS unread_count FROM messages JOIN users ON messages.sender_id = users.id WHERE messages.receiver_id = ? AND messages.is_read = 0 GROUP BY messages.sender_id, users.username;"
                                     ,session["user_id"])
    return render_template("search.html",unread_messages=unread_messages)


@app.route("/calendar")
@login_required
def calendar():
    tasks = db.execute("SELECT due_date FROM tasks WHERE user_id = ?"
                       ,session["user_id"])

    return render_template("calendar.html", tasks=tasks)

@app.route("/timer")
@login_required
def timer():
    return render_template("timer.html")

@app.route("/timer/status")
@login_required
def timer_status():

    timer = db.execute(
        "SELECT status, end_time, remaining FROM timers WHERE user_id = ?",
        session["user_id"])

    if not timer:
        return jsonify({
            "status": "stopped",
            "end_time": None,
            "remaining": 0
        })

    timer = timer[0]

    if timer["status"] == "running":

        remaining = max(
            0,
            int(timer["end_time"] - time.time())
        )

        if remaining == 0:

            db.execute(" UPDATE timers SET status = ?, remaining = ?, end_time = NULL WHERE user_id = ?",
                "finished",
                0,
                session["user_id"])

            return jsonify({
                "status": "finished",
                "end_time": None,
                "remaining": 0
            })

        return jsonify({
            "status": "running",
            "end_time": None,
            "remaining": remaining
        })

    return jsonify({
        "status": timer["status"],
        "end_time": None,
        "remaining": timer["remaining"]
    })


@app.route("/timer/start", methods=["POST"])
@login_required
def timer_start():

    data = request.get_json()
    duration = int(data["duration"])

    end_time = time.time() + duration

    db.execute(" INSERT INTO timers (user_id, status, end_time, remaining) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE status = VALUES(status), end_time = VALUES(end_time), remaining = VALUES(remaining)",
    session["user_id"],
    "running",
    end_time,
    duration)

    return jsonify({
        "status": "running",
        "end_time": end_time,
        "remaining": duration
    })


@app.route("/timer/pause", methods=["POST"])
@login_required
def timer_pause():

    timer = db.execute("SELECT status, end_time, remaining FROM timers WHERE user_id = ?",
        session["user_id"])
    if not timer:
        return jsonify({
            "status": "stopped",
            "remaining": 0
        })
    timer = timer[0]
    if timer["status"] == "running":
        remaining = max(
            0,
            int(timer["end_time"] - time.time())
        )

        db.execute(" UPDATE timers SET status = ?, remaining = ?, end_time = NULL WHERE user_id = ?",
            "paused",
            remaining,
            session["user_id"])
        return jsonify({
            "status": "paused",
            "remaining": remaining
        })
    elif timer["status"] == "paused":
        remaining = timer["remaining"]
        end_time = time.time() + remaining
        db.execute(" UPDATE timers SET status = ?, remaining = ?, end_time = ? WHERE user_id = ?",
            "running",
            remaining,
            end_time,
            session["user_id"])
        return jsonify({
            "status": "running",
            "remaining": remaining
        })
    return jsonify({
        "status": timer["status"],
        "remaining": timer["remaining"]
    })


@app.route("/timer/stop", methods=["POST"])
@login_required
def timer_stop():
    db.execute(" UPDATE timers SET status = ?, remaining = ?, end_time = NULL WHERE user_id = ?",
    "stopped",
    0,
    session["user_id"])

    return jsonify({
        "status": "stopped",
        "remaining": 0
    })

