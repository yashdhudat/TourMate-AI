# app.py (final)
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
from recommend import get_recommendations
from datetime import datetime
import pytz


# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "persona_trip.db"
SCHEMA_PATH = BASE_DIR / "db_schema.sql"

# --- Flask app ---
app = Flask(__name__)
# Use env var if provided; otherwise a default (replace with strong secret in production)
app.secret_key = os.getenv("FLASK_SECRET", "change_this_secret_for_production")

# --- Database helpers ---
def get_db():
    if not hasattr(g, "_database"):
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        g._database = conn
    return g._database

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"db_schema.sql not found at {SCHEMA_PATH}")
    db = sqlite3.connect(str(DB_PATH))
    with open(SCHEMA_PATH, "r", encoding="utf8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()

# Initialize DB if missing
if not DB_PATH.exists():
    init_db()
    print("Initialized DB at", DB_PATH)

# --- Routes: Authentication ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields", "warning")
            return render_template("register.html")

        db = get_db()
        cur = db.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            flash("Email already registered. Try logging in.", "danger")
            return render_template("register.html")

        pw_hash = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        cur = db.execute("SELECT id, username, password_hash FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        if row and check_password_hash(row["password_hash"], password):
            session.clear()
            session["user_id"] = row["id"]
            session["username"] = row["username"]
            db.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow().isoformat(), row["id"]))
            db.commit()

            # ✅ Redirect to Personality Quiz FIRST
            flash("Login successful, please complete your personality quiz.", "success")
            return redirect(url_for("quiz"))

        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))

# --- Home & quiz routes ---
@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))  # Force login before accessing home
    return render_template("index.html", username=session.get("username"))


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        # Read 1-5 scale numeric fields
        try:
            o = float(request.form.get("openness", 3))
            c = float(request.form.get("conscientiousness", 3))
            e = float(request.form.get("extraversion", 3))
            a = float(request.form.get("agreeableness", 3))
            n = float(request.form.get("neuroticism", 3))
        except ValueError:
            flash("Invalid input for quiz.", "danger")
            return render_template("quiz.html", username=session.get("username"))

        # normalize 1-5 -> 0.0-1.0
        def normalize(x):
            return max(0.0, min(1.0, (x - 1.0) / 4.0))

        pers_vec = {
            "openness": normalize(o),
            "conscientiousness": normalize(c),
            "extraversion": normalize(e),
            "agreeableness": normalize(a),
            "neuroticism": normalize(n),
        }

        # Save to DB if logged in
        if session.get("user_id"):
            db = get_db()
            # upsert into personality (user_id is primary key)
            db.execute(
                """
                INSERT INTO personality (user_id, openness, conscientiousness, extraversion, agreeableness, neuroticism, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    openness=excluded.openness,
                    conscientiousness=excluded.conscientiousness,
                    extraversion=excluded.extraversion,
                    agreeableness=excluded.agreeableness,
                    neuroticism=excluded.neuroticism,
                    updated_at=excluded.updated_at
                """,
                (
                    session["user_id"],
                    pers_vec["openness"],
                    pers_vec["conscientiousness"],
                    pers_vec["extraversion"],
                    pers_vec["agreeableness"],
                    pers_vec["neuroticism"],
                    datetime.utcnow().isoformat(),
                ),
            )
            db.commit()
            flash("Personality saved to your profile.", "success")
        else:
            flash("Personality recorded for this session. Login to save permanently.", "info")

        session["personality"] = pers_vec
        return redirect(url_for("index"))

    return render_template("quiz.html", username=session.get("username"))

# --- Recommendation route ---
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    # Check if user clicked "See More"
    show_more = request.args.get("more") == "true"

    # If POST → user submitted new preferences
    if request.method == "POST":
        # --- Build user_input dictionary ---
        user_input = {
            "Climate_Moderate": int(request.form.get("climate") == "Moderate"),
            "Climate_Cold": int(request.form.get("climate") == "Cold"),
            "Climate_Warm": int(request.form.get("climate") == "Warm"),
            "Budget_Low": int(request.form.get("budget") == "Low"),
            "Budget_Medium": int(request.form.get("budget") == "Medium"),
            "Budget_High": int(request.form.get("budget") == "High"),
            "Solo": int("Solo" in request.form.getlist("travel_type")),
            "Couple": int("Couple" in request.form.getlist("travel_type")),
            "Family": int("Family" in request.form.getlist("travel_type")),
            "Group": int("Group" in request.form.getlist("travel_type")),
        }

        # Activities
        activities = [
            "Beaches", "Culture", "Food", "History", "Nature", "Nightlife",
            "Photography", "Relaxation", "Safari", "Shopping", "Sightseeing",
            "Spiritual", "Trekking", "Adventure"
        ]
        selected = request.form.getlist("activities")
        for activity in activities:
            user_input[activity] = int(activity in selected)

        # Save user_input in session so pagination still works
        session["last_user_input"] = user_input

    else:
        # GET request → for "See More Suggestions"
        user_input = session.get("last_user_input")

        if not user_input:
            flash("Please fill the form first.", "warning")
            return redirect("/")

    # ---- Get personality (DB or session) ----
    personality_data = None
    if session.get("user_id"):
        db = get_db()
        row = db.execute(
            "SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism FROM personality WHERE user_id = ?",
            (session["user_id"],)
        ).fetchone()
        if row:
            personality_data = {
                "openness": row["openness"],
                "conscientiousness": row["conscientiousness"],
                "extraversion": row["extraversion"],
                "agreeableness": row["agreeableness"],
                "neuroticism": row["neuroticism"],
            }

    if not personality_data:
        personality_data = session.get("personality")

    # ---- Call new recommendation function ----
    recommendations = get_recommendations(
        user_input=user_input,
        user_personality=personality_data,
        show_more=show_more
    )

    # ---- Save history only when POST (first page) ----
    if request.method == "POST" and session.get("user_id"):
        db = get_db()
        ts = datetime.utcnow().isoformat()
        for rec in recommendations:
            db.execute(
                "INSERT INTO history (user_id, destination, country, score, params_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session["user_id"],
                    rec["destination"],
                    rec["state"],   # <– rec["state"] still correct, but stored under 'country'
                    rec["final_score"],
                    json.dumps(user_input),
                    ts,
                )
            )
        db.commit()

    return render_template(
        "results.html",
        recommendations=recommendations,
        show_more=show_more,
        username=session.get("username")
    )

# --- History view ---
@app.route("/history")
def history():
    if not session.get("user_id"):
        flash("Please log in to view history.", "info")
        return redirect(url_for("login"))

    db = get_db()
    rows = db.execute(
    "SELECT id, destination, country, score, params_json, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
    (session["user_id"],)
    ).fetchall()
    history = [dict(r) for r in rows]
    return render_template("history.html", history=history, username=session.get("username"))

@app.route("/history/delete/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = get_db()
    db.execute(
        "DELETE FROM history WHERE id = ? AND user_id = ?", 
        (history_id, session["user_id"])
    )
    db.commit()

    flash("Entry deleted successfully.", "success")
    return redirect(url_for("history"))


@app.template_filter("pretty_ist")
def pretty_ist(value):
    try:
        # parse stored UTC ISO timestamp
        dt_utc = datetime.fromisoformat(value)

        # convert UTC → IST
        utc_zone = pytz.timezone("UTC")
        ist_zone = pytz.timezone("Asia/Kolkata")

        dt_utc = utc_zone.localize(dt_utc)
        dt_ist = dt_utc.astimezone(ist_zone)

        # pretty format
        return dt_ist.strftime("🕒 %d %b %Y • %I:%M %p")
    except Exception as e:
        return value



# Run app
if __name__ == "__main__":
    app.run(debug=True)
