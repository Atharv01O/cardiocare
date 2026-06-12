"""
CardioCare — Main Flask Application
"""

import os
from datetime import datetime

from flask import (Flask, render_template, request, redirect,
                   url_for, send_file, jsonify, flash)
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from pymongo import MongoClient
from bson import ObjectId

from config import (MONGO_URI, MONGO_DB, MONGO_COL,
                    REPORTS_DIR, DEBUG, SECRET_KEY)
from utils.predictor        import run_prediction
from utils.risk_engine      import analyze_risk
from utils.pdf_generator    import create_pdf
from utils.gemini_chat      import chat_with_gemini
from utils.who_api          import get_who_cvd_data
from utils.comparator       import compare_reports
from utils.auth             import create_user, get_user_by_email, get_user_by_id
from utils.blood_analyser   import analyse_blood_report

from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://atharvadevrukhkar13_db_user:YOUR_NEW_PASSWORD@m0cluster.quzgmpk.mongodb.net/cardiocare?retryWrites=true&w=majority"
)

db = client["cardiocare"]
users_collection = db["users"]
# =========================
# INIT
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Flask-Login ────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view    = "login"
login_manager.login_message = "Please log in to access CardioCare."

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# ── MongoDB ────────────────────────────────────────────────────
client     = MongoClient(MONGO_URI)
db         = client[MONGO_DB]
collection = db[MONGO_COL]

def _clean(reports):
    for r in reports:
        r["_id"] = str(r["_id"])
    return reports


# =========================
# AUTH ROUTES
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user     = get_user_by_email(email, password)
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        name     = request.form.get("name", "").strip()
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("signup.html")
        ok, msg = create_user(email, password, name)
        if ok:
            user = get_user_by_email(email, password)
            login_user(user)
            return redirect(url_for("dashboard"))
        flash(msg, "error")
    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =========================
# DASHBOARD  /
# =========================

@app.route("/")
@login_required
def dashboard():
    reports  = _clean(list(
        collection.find({"user_id": current_user.id}).sort("date", -1)
    ))
    total    = len(reports)
    low      = sum(1 for r in reports if r.get("risk") == "Low Risk")
    moderate = sum(1 for r in reports if r.get("risk") == "Moderate Risk")
    high     = sum(1 for r in reports if r.get("risk") == "High Risk")
    recent_scores = [r["score"] for r in reports[:10]][::-1]
    return render_template(
        "dashboard.html",
        reports=reports[:6], total=total, low=low,
        moderate=moderate, high=high, recent_scores=recent_scores,
    )


# =========================
# PREDICT  /predict
# =========================

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    if request.method == "GET":
        return render_template("predict.html")

    fields = ["age","sex","cp","trestbps","chol","fbs","restecg",
              "thalach","exang","oldpeak","slope","ca","thal"]
    try:
        values = [float(request.form.get(f, 0)) for f in fields]
    except ValueError:
        return render_template("predict.html", error="Please enter valid numeric values.")

    prob     = run_prediction(values)
    score    = round(prob * 100, 2)
    analysis = analyze_risk(score)

    filename = f"report_{int(datetime.now().timestamp())}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, filename)

    report_doc = {
        "user_id"  : current_user.id,
        "score"    : score,
        "risk"     : analysis["level"],
        "icon"     : analysis["icon"],
        "message"  : analysis["message"],
        "symptoms" : analysis["symptoms"],
        "care"     : analysis["care"],
        "values"   : values,
        "pdf"      : filename,
        "date"     : datetime.now().strftime("%d-%m-%Y %H:%M"),
    }

    create_pdf(report_doc, pdf_path)
    inserted     = collection.insert_one(report_doc)
    new_id       = str(inserted.inserted_id)
    values_dict  = dict(zip(fields, values))

    past_reports = _clean(list(
        collection.find({"user_id": current_user.id,
                         "_id": {"$ne": inserted.inserted_id}}).sort("date", -1).limit(20)
    ))

    return render_template(
        "result.html",
        score=score, analysis=analysis, pdf_file=filename,
        values=values_dict, new_id=new_id, past_reports=past_reports,
    )


# =========================
# HISTORY  /history
# =========================

@app.route("/history")
@login_required
def history():
    reports = _clean(list(
        collection.find({"user_id": current_user.id}).sort("date", -1)
    ))
    return render_template("history.html", reports=reports)


# =========================
# DELETE  /delete/<id>
# =========================

@app.route("/delete/<report_id>")
@login_required
def delete_report(report_id):
    collection.delete_one({"_id": ObjectId(report_id), "user_id": current_user.id})
    return redirect(url_for("history"))


# =========================
# BLOOD REPORT  /blood-report
# =========================

@app.route("/blood-report", methods=["GET", "POST"])
@login_required
def blood_report():
    if request.method == "GET":
        return render_template("blood_report.html")

    file = request.files.get("report_file")
    if not file or file.filename == "":
        return render_template("blood_report.html", error="Please upload a file.")

    allowed = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}
    mime    = file.mimetype
    if mime not in allowed:
        return render_template("blood_report.html",
                               error="Only PDF, JPG, or PNG files are supported.")

    file_bytes = file.read()
    result     = analyse_blood_report(file_bytes, mime)

    return render_template("blood_report.html", result=result, filename=file.filename)


# =========================
# MODEL INFO  /model
# =========================

@app.route("/model")
@login_required
def model_info():
    return render_template("model.html")


# =========================
# COMPARE  /compare
# =========================

@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    all_reports = _clean(list(
        collection.find({"user_id": current_user.id}).sort("date", -1)
    ))
    if request.method == "GET":
        return render_template("compare.html", all_reports=all_reports, result=None)

    new_id = request.form.get("new_id")
    old_id = request.form.get("old_id")

    if not new_id or not old_id or new_id == old_id:
        return render_template("compare.html", all_reports=all_reports, result=None,
                               error="Please select two different reports.")
    try:
        new_report = collection.find_one({"_id": ObjectId(new_id), "user_id": current_user.id})
        old_report = collection.find_one({"_id": ObjectId(old_id), "user_id": current_user.id})
    except Exception:
        return redirect(url_for("history"))

    if not new_report or not old_report:
        return redirect(url_for("history"))

    new_report["_id"] = str(new_report["_id"])
    old_report["_id"] = str(old_report["_id"])
    result = compare_reports(new_report, old_report)

    return render_template("compare.html", result=result,
                           new_report=new_report, old_report=old_report,
                           all_reports=all_reports)


# =========================
# GEMINI CHAT  /api/chat
# =========================

@app.route("/api/chat", methods=["POST"])
@login_required
def gemini_chat():
    data           = request.get_json()
    messages       = data.get("messages", [])
    report_context = data.get("report_context", None)
    if not messages:
        return jsonify({"reply": "Please send a message."}), 400
    reply = chat_with_gemini(messages, report_context)
    return jsonify({"reply": reply})


# =========================
# WHO API  /api/who-data
# =========================

@app.route("/api/who-data")
@login_required
def who_data():
    return jsonify(get_who_cvd_data())


# =========================
# DOWNLOAD  /download/<filename>
# =========================

@app.route("/download/<filename>")
@login_required
def download(filename):
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        return "File not found", 404
    return send_file(path, as_attachment=True)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=DEBUG)
