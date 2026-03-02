from dotenv import load_dotenv
load_dotenv()
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

import pdfplumber
import re
import os

# ====================== APP CONFIG ======================

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

# ====================== DATABASE MODEL ======================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ====================== ROUTES ======================

@app.route("/")
def home():
    return redirect(url_for("login_page"))

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))

# ====================== AUTH ======================

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Signup successful"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password, data["password"]):
        login_user(user)
        return jsonify({"message": "Login successful"})

    return jsonify({"message": "Invalid credentials"}), 401

# ====================== ANALYZE ======================

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    try:
        file = request.files.get("resume")
        jd_text = request.form.get("jobDescription", "")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # ===== Extract Resume Text =====
        resume_text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""

        resume_text = resume_text.lower()
        jd_text = jd_text.lower()

        # ===== Normalize Function =====
        def normalize(text):
            text = text.lower()
            text = text.replace("c++", "cpp")
            text = text.replace("rest api", "restapi")
            return text

        resume_norm = normalize(resume_text)
        jd_norm = normalize(jd_text)

        # ===== Cosine Similarity =====
        documents = [resume_norm, jd_norm if jd_norm else resume_norm]

        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)

        cosine_sim = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        cosine_score = round(cosine_sim * 100, 2)

        # ===== Skill Matching =====
        skill_keywords = [
            "python", "sql", "machine learning", "data analysis",
            "excel", "java", "docker", "flask",
            "django", "react", "cpp", "tensorflow",
            "aws", "power bi", "pandas", "numpy"
        ]

        matched_skills = []
        missing_skills = []
        heatmap_data = []

        for skill in skill_keywords:
            count = resume_norm.count(skill)

            if count > 0:
                matched_skills.append(skill)
                heatmap_data.append({
                    "skill": skill,
                    "count": count
                })
            else:
                missing_skills.append(skill)

        skill_score = min(len(matched_skills) * 8, 100)

        # ===== JD Match Score =====
        # JD MATCH BASED ONLY ON SKILLS

        jd_skill_matches = 0
        jd_skill_total = 0

        for skill in skill_keywords:
          if skill in jd_norm:
             jd_skill_total += 1
          if skill in resume_norm:
             jd_skill_matches += 1

        jd_score = round(
           (jd_skill_matches / jd_skill_total) * 100,
            2
        ) if jd_skill_total else 0

        # ===== ATS Score =====
        ats_score = round((skill_score + cosine_score) / 2, 2)

        # ===== Final Score =====
        final_score = round(
            (skill_score + cosine_score + jd_score) / 3,
            2
        )

        # ===== Resume Strength =====
        if final_score >= 85:
            strength = "Excellent"
        elif final_score >= 70:
            strength = "Strong"
        elif final_score >= 50:
            strength = "Moderate"
        else:
            strength = "Weak"

        # ===== Suggestions Engine =====
        suggestions = ""

        if skill_score < 60:
            suggestions += "• Add more technical skills.\n"
        if cosine_score < 60:
            suggestions += "• Improve alignment with job description.\n"
        if jd_score < 60:
            suggestions += "• Include more JD-related keywords.\n"
        if missing_skills:
            suggestions += "• Consider adding: " + ", ".join(missing_skills[:5]) + "\n"

        if suggestions == "":
            suggestions = "Your resume is strongly aligned with the job."

        return jsonify({
            "final_score": final_score,
            "skills_score": skill_score,
            "experience_score": 70,
            "ats_score": ats_score,
            "cosine_match_score": cosine_score,
            "intelligent_jd_score": jd_score,
            "strength_label": strength,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "heatmap_data": heatmap_data,
            "enhanced_text": suggestions
        })

    except Exception as e:
        print("ANALYZE ERROR:", e)
        return jsonify({"error": "Analysis failed"}), 500

# ====================== SAVE REPORT ======================

@app.route("/save_report", methods=["POST"])
@login_required
def save_report():

    try:
        data = request.get_json()

        file_path = "resume_report.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=letter)

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor("#00AEEF"),
            spaceAfter=20
        )

        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor("#1F4E79"),
            spaceAfter=10
        )

        elements.append(Paragraph("Resume Analysis Report", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph(
            f"Generated for: {current_user.email}",
            styles["Normal"]
        ))

        elements.append(Paragraph(
            f"Date: {datetime.now().strftime('%d %B %Y')}",
            styles["Normal"]
        ))

        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("Resume Strength", section_style))
        elements.append(Paragraph(
            f"{data.get('strength_label')} ({data.get('final_score')}/100)",
            styles["Normal"]
        ))

        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Score Breakdown", section_style))

        table_data = [
            ["Metric", "Score"],
            ["Final Score", data.get("final_score")],
            ["Skills Score", data.get("skills_score")],
            ["ATS Score", data.get("ats_score")],
            ["Cosine Similarity", data.get("cosine_match_score")],
            ["JD Match Score", data.get("intelligent_jd_score")]
        ]

        table = Table(table_data, colWidths=[3 * inch, 1.5 * inch])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#00AEEF")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("Matched Skills", section_style))
        elements.append(Paragraph(", ".join(data.get("matched_skills", [])), styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("Missing Skills", section_style))
        elements.append(Paragraph(", ".join(data.get("missing_skills", [])), styles["Normal"]))
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("Improvement Suggestions", section_style))
        elements.append(Paragraph(data.get("enhanced_text"), styles["Normal"]))

        doc.build(elements)

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        print("PDF ERROR:", e)
        return jsonify({"error": "PDF generation failed"}), 500

# ====================== RUN ======================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)