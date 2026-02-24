# app.py
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from recommend import get_recommendations
import pytz

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "persona_trip.db"
SCHEMA_PATH = BASE_DIR / "db_schema.sql"

# --- Flask app ---
app = Flask(__name__)
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

if not DB_PATH.exists():
    init_db()
    print("Initialized DB at", DB_PATH)


# ═══════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Please fill in all fields", "warning")
            return render_template("register.html")

        db = get_db()
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash("Email already registered. Try logging in.", "danger")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        db.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        row = db.execute(
            "SELECT id, username, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

        if row and check_password_hash(row["password_hash"], password):
            session.clear()
            session["user_id"]  = row["id"]
            session["username"] = row["username"]
            db.execute("UPDATE users SET last_login = ? WHERE id = ?",
                       (datetime.utcnow().isoformat(), row["id"]))
            db.commit()
            flash("Login successful, please complete your personality quiz.", "success")
            return redirect(url_for("quiz"))

        flash("Invalid credentials", "danger")
    return render_template("login.html", username=session.get("username"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


# ═══════════════════════════════════════
#  HOME
# ═══════════════════════════════════════

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("index.html", username=session.get("username"))


# ═══════════════════════════════════════
#  QUIZ  — now uses 10 questions → auto OCEAN scores
# ═══════════════════════════════════════

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "POST":
        try:
            # Read all 10 answers (1-5 scale)
            q = {i: float(request.form.get(f"q{i}", 3)) for i in range(1, 11)}
        except ValueError:
            flash("Invalid input. Please answer all questions.", "danger")
            return render_template("quiz.html", username=session.get("username"))

        # ── Map questions to OCEAN traits ──
        # Q1, Q2  → Openness
        # Q3, Q4  → Conscientiousness
        # Q5, Q6  → Extraversion
        # Q7, Q8  → Agreeableness
        # Q9, Q10 → Neuroticism
        def avg_normalize(*vals):
            avg = sum(vals) / len(vals)
            return round(max(0.0, min(1.0, (avg - 1.0) / 4.0)), 4)

        pers_vec = {
            "openness":          avg_normalize(q[1], q[2]),
            "conscientiousness": avg_normalize(q[3], q[4]),
            "extraversion":      avg_normalize(q[5], q[6]),
            "agreeableness":     avg_normalize(q[7], q[8]),
            "neuroticism":       avg_normalize(q[9], q[10]),
        }

        # Save to DB if logged in
        if session.get("user_id"):
            db = get_db()
            db.execute(
                """
                INSERT INTO personality
                  (user_id, openness, conscientiousness, extraversion, agreeableness, neuroticism, updated_at)
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
                    pers_vec["openness"], pers_vec["conscientiousness"],
                    pers_vec["extraversion"], pers_vec["agreeableness"],
                    pers_vec["neuroticism"],
                    datetime.utcnow().isoformat(),
                ),
            )
            db.commit()
            flash("Personality profile saved! 🧠", "success")
        else:
            flash("Personality recorded for this session. Login to save permanently.", "info")

        session["personality"] = pers_vec
        return redirect(url_for("index"))

    return render_template("quiz.html", username=session.get("username"))


# ═══════════════════════════════════════
#  RECOMMENDATIONS
# ═══════════════════════════════════════

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    show_more = request.args.get("more") == "true"

    if request.method == "POST":
        user_input = {
            "Climate_Moderate": int(request.form.get("climate") == "Moderate"),
            "Climate_Cold":     int(request.form.get("climate") == "Cold"),
            "Climate_Warm":     int(request.form.get("climate") == "Warm"),
            "Budget_Low":       int(request.form.get("budget") == "Low"),
            "Budget_Medium":    int(request.form.get("budget") == "Medium"),
            "Budget_High":      int(request.form.get("budget") == "High"),
            "Solo":   int("Solo"   in request.form.getlist("travel_type")),
            "Couple": int("Couple" in request.form.getlist("travel_type")),
            "Family": int("Family" in request.form.getlist("travel_type")),
            "Group":  int("Group"  in request.form.getlist("travel_type")),
        }
        activities = ["Beaches","Culture","Food","History","Nature","Nightlife",
                      "Photography","Relaxation","Safari","Shopping","Sightseeing",
                      "Spiritual","Trekking","Adventure"]
        selected = request.form.getlist("activities")
        for act in activities:
            user_input[act] = int(act in selected)

        session["last_user_input"] = user_input
    else:
        user_input = session.get("last_user_input")
        if not user_input:
            flash("Please fill the form first.", "warning")
            return redirect("/")

    # Load personality
    personality_data = None
    if session.get("user_id"):
        db = get_db()
        row = db.execute(
            "SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism "
            "FROM personality WHERE user_id = ?", (session["user_id"],)
        ).fetchone()
        if row:
            personality_data = dict(row)

    if not personality_data:
        personality_data = session.get("personality")

    recommendations = get_recommendations(
        user_input=user_input,
        user_personality=personality_data,
        show_more=show_more,
        use_ai=True
    )

    # Save history on first POST
    if request.method == "POST" and session.get("user_id"):
        db = get_db()
        ts = datetime.utcnow().isoformat()
        for rec in recommendations:
            db.execute(
                "INSERT INTO history (user_id, destination, country, score, params_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session["user_id"], rec["destination"], rec["state"],
                 rec["final_score"], json.dumps(user_input), ts),
            )
        db.commit()

    return render_template("results.html",
                           recommendations=recommendations,
                           show_more=show_more,
                           username=session.get("username"))


# ═══════════════════════════════════════
#  AI ITINERARY  — NEW
#  GET /itinerary/<destination>?state=<state>
# ═══════════════════════════════════════

@app.route("/itinerary/<destination>")
def itinerary(destination):
    if not session.get("user_id"):
        flash("Please log in to generate an itinerary.", "info")
        return redirect(url_for("login"))

    state = request.args.get("state", "")
    days  = int(request.args.get("days", 3))

    # Load personality & last preferences
    personality_data = None
    db = get_db()
    row = db.execute(
        "SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism "
        "FROM personality WHERE user_id = ?", (session["user_id"],)
    ).fetchone()
    if row:
        personality_data = dict(row)

    user_input = session.get("last_user_input", {})

    try:
        from ai_utils import generate_itinerary
        itinerary_data = generate_itinerary(
            destination=destination,
            state=state,
            personality=personality_data,
            user_input=user_input,
            days=days
        )
    except Exception as e:
        print(f"[itinerary error] {e}")
        itinerary_data = None

    return render_template("itinerary.html",
                           itinerary=itinerary_data,
                           destination=destination,
                           state=state,
                           username=session.get("username"))


# ═══════════════════════════════════════
#  DESTINATION CHATBOT  — NEW
#  POST /chat  (JSON API)
# ═══════════════════════════════════════

@app.route("/chat", methods=["POST"])
def chat():
    data        = request.get_json()
    destination = data.get("destination", "")
    state       = data.get("state", "")
    question    = data.get("question", "").strip()

    if not question or not destination:
        return jsonify({"answer": "Please provide a destination and a question."})

    # Load personality for personalised answers
    personality_data = None
    if session.get("user_id"):
        db = get_db()
        row = db.execute(
            "SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism "
            "FROM personality WHERE user_id = ?", (session["user_id"],)
        ).fetchone()
        if row:
            personality_data = dict(row)

    try:
        from ai_utils import destination_chat
        answer = destination_chat(
            destination=destination,
            state=state,
            question=question,
            personality=personality_data
        )
    except Exception as e:
        print(f"[chat error] {e}")
        answer = "I'm having trouble connecting right now. Please try again!"

    return jsonify({"answer": answer})


# ═══════════════════════════════════════
#  HISTORY
# ═══════════════════════════════════════

@app.route("/history")
def history():
    if not session.get("user_id"):
        flash("Please log in to view history.", "info")
        return redirect(url_for("login"))

    db   = get_db()
    rows = db.execute(
        "SELECT id, destination, country, score, params_json, created_at "
        "FROM history WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    return render_template("history.html",
                           history=[dict(r) for r in rows],
                           username=session.get("username"))


@app.route("/history/delete/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    get_db().execute("DELETE FROM history WHERE id = ? AND user_id = ?",
                     (history_id, session["user_id"]))
    get_db().commit()
    flash("Entry deleted.", "success")
    return redirect(url_for("history"))


# ═══════════════════════════════════════
#  TEMPLATE FILTER
# ═══════════════════════════════════════

@app.template_filter("pretty_ist")
def pretty_ist(value):
    try:
        dt_utc = datetime.fromisoformat(value)
        ist    = pytz.timezone("Asia/Kolkata")
        dt_ist = pytz.utc.localize(dt_utc).astimezone(ist)
        return dt_ist.strftime("🕒 %d %b %Y • %I:%M %p")
    except Exception:
        return value


if __name__ == "__main__":
    app.run(debug=True)