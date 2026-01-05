import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from openai import OpenAI

# ---------------- BASIC APP ----------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "diasure-secret")

# ---------------- LOGIN ----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "google.login"

users = {}

class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# ---------------- GOOGLE LOGIN ----------------
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/google_login"
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    info = resp.json()

    user = User(info["id"], info["name"], info["email"])
    users[user.id] = user
    login_user(user)

    return redirect(url_for("dashboard"))

# ---------------- OPENAI ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEDICAL_DISCLAIMER = (
    "DISCLAIMER: This tool provides general educational guidance only. "
    "It does NOT replace professional medical advice, diagnosis, or treatment."
)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=current_user.name)

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    sugar = request.json.get("sugar")

    prompt = f"""
A patient has a fasting blood sugar of {sugar} mg/dL.

1. Explain what this level means.
2. Give practical food guidance for today.
3. Keep advice safe and medically sound.
4. Use numbered tips with headings.
5. No diagnosis, no medication changes.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    ai_text = response.output_text

    formatted = ai_text.replace(
        "1.", "<span class='tip'>1.</span>"
    )

    return jsonify({
        "result": formatted + f"<br><br><span class='disclaimer'>{MEDICAL_DISCLAIMER}</span>"
    })

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
