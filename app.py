from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from mysql.connector import Error
from PyPDF2 import PdfReader
import os
import re

app = Flask(__name__)

app.secret_key = "skillbridge_secret_key_2026"

# -----------------------------
# UPLOAD SETTINGS
# -----------------------------
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Skill@2026",
            database="skillbridge"
        )

        return connection

    except Error as e:
        print("Database connection error:", e)
        return None


# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():

    connection = get_db_connection()

    if connection is None:
        return

    cursor = connection.cursor()

    try:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_resumes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255),
                resume_text LONGTEXT,
                extracted_skills TEXT,
                skill_score INT DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_skills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                skill_name VARCHAR(100),
                skill_level INT DEFAULT 0,
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
            )
        """)

        connection.commit()

        print("Database tables ready.")

    except Error as e:

        print("Table creation error:", e)
        connection.rollback()

    finally:

        cursor.close()
        connection.close()


# =========================================================
# AI / NLP SKILL DATABASE
# =========================================================

SKILLS = {

    "Python": [
        "python",
        "python programming"
    ],

    "C": [
        "c programming",
        "c language"
    ],

    "C++": [
        "c++",
        "cpp",
        "c plus plus"
    ],

    "Java": [
        "java programming",
        "java developer"
    ],

    "HTML": [
        "html",
        "html5"
    ],

    "CSS": [
        "css",
        "css3"
    ],

    "JavaScript": [
        "javascript",
        "ecmascript"
    ],

    "React": [
        "react",
        "reactjs",
        "react.js"
    ],

    "Node.js": [
        "node.js",
        "nodejs",
        "node js"
    ],

    "Flask": [
        "flask"
    ],

    "Django": [
        "django"
    ],

    "SQL": [
        "sql",
        "structured query language"
    ],

    "MySQL": [
        "mysql"
    ],

    "MongoDB": [
        "mongodb",
        "mongo db"
    ],

    "Machine Learning": [
        "machine learning"
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "artificial intelligence ai"
    ],

    "NLP": [
        "natural language processing",
        "nlp"
    ],

    "Deep Learning": [
        "deep learning",
        "neural network",
        "neural networks"
    ],

    "Data Science": [
        "data science",
        "data scientist"
    ],

    "Pandas": [
        "pandas"
    ],

    "NumPy": [
        "numpy"
    ],

    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],

    "Git": [
        "git",
        "version control"
    ],

    "GitHub": [
        "github",
        "git hub"
    ],

    "REST API": [
        "rest api",
        "restful api"
    ],

    "Bootstrap": [
        "bootstrap"
    ],

    "Data Entry": [
        "data entry"
    ],

    "MS Word": [
        "ms word",
        "microsoft word"
    ],

    "Excel": [
        "excel"
    ],

    "Communication": [
        "communication skills",
        "communication"
    ],

    "Leadership": [
        "leadership"
    ],

    "Problem Solving": [
        "problem solving",
        "problem-solving"
    ]
}


# Skills required for the SkillBridge learning path
REQUIRED_SKILLS = [
    "Python",
    "HTML",
    "CSS",
    "JavaScript",
    "SQL",
    "Git",
    "GitHub",
    "Flask",
    "Machine Learning"
]


# =========================================================
# NLP FUNCTIONS
# =========================================================

def clean_text(text):

    text = text or ""

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text):

    text = clean_text(text)

    detected_skills = []

    for skill, keywords in SKILLS.items():

        for keyword in keywords:

            pattern = (
                r"(?<!\w)"
                + re.escape(keyword.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, text):

                detected_skills.append(skill)

                break

    return detected_skills


# =========================================================
# AI SKILL LEVEL ESTIMATION
# =========================================================

def calculate_skill_level(skill, resume_text):

    text = clean_text(resume_text)

    score = 40

    experience_words = [
        "project",
        "experience",
        "internship",
        "intern",
        "developed",
        "built",
        "implemented",
        "worked",
        "created",
        "deployed"
    ]

    advanced_words = [
        "advanced",
        "professional",
        "expert",
        "production",
        "optimization"
    ]

    for word in experience_words:

        if word in text:
            score += 4

    for word in advanced_words:

        if word in text:
            score += 5

    return min(score, 95)


# =========================================================
# AI OVERALL SKILL SCORE
# =========================================================

def calculate_skill_score(skills):

    if not skills:
        return 0

    score = round((len(skills) / 12) * 100)

    return min(score, 100)


# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

def calculate_skill_gaps(skills):

    student_skills = {
        skill.lower()
        for skill in skills
    }

    gaps = []

    for required in REQUIRED_SKILLS:

        if required.lower() not in student_skills:

            gaps.append(required)

    return gaps


# =========================================================
# LEARNING RECOMMENDATIONS
# =========================================================

LEARNING_PATHS = {

    "Python": (
        "Python Programming",
        "Strengthen Python programming, functions, OOP and problem solving.",
        "Beginner → Intermediate"
    ),

    "HTML": (
        "HTML Fundamentals",
        "Learn semantic HTML and structured web page development.",
        "Beginner → Intermediate"
    ),

    "CSS": (
        "CSS & Responsive Design",
        "Improve layouts, styling and responsive web design.",
        "Beginner → Intermediate"
    ),

    "JavaScript": (
        "JavaScript Fundamentals",
        "Learn DOM manipulation, events and frontend interactivity.",
        "Beginner → Intermediate"
    ),

    "SQL": (
        "SQL & Databases",
        "Build strong SQL queries and database fundamentals.",
        "Beginner → Intermediate"
    ),

    "Git": (
        "Git & Version Control",
        "Learn commits, branches, merge and professional workflows.",
        "Beginner → Intermediate"
    ),

    "GitHub": (
        "GitHub",
        "Learn repositories, collaboration, branches and pull requests.",
        "Beginner → Intermediate"
    ),

    "Flask": (
        "Flask Web Development",
        "Build Python web applications using Flask.",
        "Beginner → Intermediate"
    ),

    "Machine Learning": (
        "Machine Learning Basics",
        "Learn supervised learning, classification and model evaluation.",
        "Beginner"
    )
}


def get_learning_recommendations(skill_gaps):

    recommendations = []

    for skill in skill_gaps:

        if skill in LEARNING_PATHS:

            title, description, level = LEARNING_PATHS[skill]

            recommendations.append({
                "title": title,
                "description": description,
                "level": level
            })

    return recommendations[:3]


# =========================================================
# OPPORTUNITIES
# =========================================================

OPPORTUNITIES = [

    {
        "title": "Software Development Intern",
        "company": "Technology Company",
        "skills": ["Python", "Flask", "SQL"],
        "logo": "T"
    },

    {
        "title": "Web Developer Intern",
        "company": "Digital Solutions",
        "skills": ["HTML", "CSS", "JavaScript"],
        "logo": "D"
    },

    {
        "title": "Python Developer Intern",
        "company": "AI Solutions",
        "skills": ["Python", "Flask", "Git"],
        "logo": "A"
    },

    {
        "title": "Machine Learning Intern",
        "company": "Data Technologies",
        "skills": ["Python", "Machine Learning", "SQL"],
        "logo": "M"
    },

    {
        "title": "Frontend Developer Intern",
        "company": "Web Technologies",
        "skills": ["HTML", "CSS", "JavaScript", "Git"],
        "logo": "W"
    }
]


def calculate_opportunities(student_skills):

    student_skills_lower = {
        skill.lower()
        for skill in student_skills
    }

    results = []

    for opportunity in OPPORTUNITIES:

        required_skills = opportunity["skills"]

        matched = 0

        for skill in required_skills:

            if skill.lower() in student_skills_lower:

                matched += 1

        match_score = round(
            (matched / len(required_skills)) * 100
        )

        result = opportunity.copy()

        result["match"] = match_score

        results.append(result)

    results.sort(
        key=lambda item: item["match"],
        reverse=True
    )

    return results


# =========================================================
# GET STUDENT DATA
# =========================================================

def get_student_data(user_id):

    data = {
        "resume": False,
        "skills": [],
        "details": [],
        "score": 0
    }

    connection = get_db_connection()

    if connection is None:
        return data

    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                extracted_skills,
                skill_score
            FROM student_resumes
            WHERE user_id = %s
            ORDER BY uploaded_at DESC
            LIMIT 1
        """, (user_id,))

        resume = cursor.fetchone()

        if resume:

            data["resume"] = True

            extracted = resume["extracted_skills"] or ""

            data["skills"] = [
                skill.strip()
                for skill in extracted.split(",")
                if skill.strip()
            ]

            data["score"] = resume["skill_score"] or 0

        cursor.execute("""
            SELECT
                skill_name,
                skill_level
            FROM student_skills
            WHERE user_id = %s
            ORDER BY skill_level DESC
        """, (user_id,))

        data["details"] = cursor.fetchall()

    except Error as e:

        print("Student data error:", e)

    finally:

        cursor.close()
        connection.close()

    return data


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        role = request.form.get(
            "role", ""
        ).strip().lower()

        if not full_name or not email or not password or not role:

            return """
            <script>
                alert("Please fill all required fields!");
                history.back();
            </script>
            """

        connection = get_db_connection()

        if connection is None:

            return """
            <script>
                alert("Database connection failed!");
                history.back();
            </script>
            """

        cursor = connection.cursor()

        try:

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                return """
                <script>
                    alert("Email already registered!");
                    history.back();
                </script>
                """

            cursor.execute("""
                INSERT INTO users
                (full_name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (
                full_name,
                email,
                password,
                role
            ))

            connection.commit()

            session["user_id"] = cursor.lastrowid
            session["full_name"] = full_name
            session["role"] = role

            if role == "student":

                return redirect(
                    url_for("student_dashboard")
                )

            return redirect(
                url_for("home")
            )

        except Error as e:

            print("Signup error:", e)

            connection.rollback()

            return """
            <script>
                alert("Signup failed!");
                history.back();
            </script>
            """

        finally:

            cursor.close()
            connection.close()

    return render_template("signup.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        role = request.form.get(
            "role", ""
        ).strip().lower()

        connection = get_db_connection()

        if connection is None:

            return """
            <script>
                alert("Database connection failed!");
                history.back();
            </script>
            """

        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute("""
                SELECT
                    id,
                    full_name,
                    email,
                    role
                FROM users
                WHERE email = %s
                AND password = %s
                AND role = %s
            """, (
                email,
                password,
                role
            ))

            user = cursor.fetchone()

            if not user:

                return """
                <script>
                    alert("Invalid email, password or role!");
                    history.back();
                </script>
                """

            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]

            if user["role"] == "student":

                return redirect(
                    url_for("student_dashboard")
                )

            return redirect(
                url_for("home")
            )

        except Error as e:

            print("Login error:", e)

            return """
            <script>
                alert("Login failed!");
                history.back();
            </script>
            """

        finally:

            cursor.close()
            connection.close()

    return render_template("login.html")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "student":

        return redirect(
            url_for("home")
        )

    user_id = session["user_id"]

    data = get_student_data(user_id)

    student_skills = data["skills"]

    skill_gaps = calculate_skill_gaps(
        student_skills
    )

    recommendations = get_learning_recommendations(
        skill_gaps
    )

    opportunities = calculate_opportunities(
        student_skills
    )

    best_match = 0

    if opportunities:

        best_match = opportunities[0]["match"]

    return render_template(
        "student-dashboard.html",

        full_name=session.get(
            "full_name",
            "Student"
        ),

        skills=student_skills,

        skill_details=data["details"],

        skill_score=data["score"],

        gaps=skill_gaps,

        skills_count=len(student_skills),

        gaps_count=len(skill_gaps),

        best_match=best_match,

        recommendations=recommendations,

        opportunities=opportunities,

        resume_uploaded=data["resume"]
    )


# =========================================================
# RESUME UPLOAD + AI/NLP ANALYSIS
# =========================================================

@app.route("/upload-resume", methods=["POST"])
def upload_resume():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("role") != "student":

        return redirect(
            url_for("home")
        )

    file = request.files.get("resume")

    if not file or file.filename == "":

        return """
        <script>
            alert("Please select a PDF resume!");
            window.location.href="/student-dashboard";
        </script>
        """

    if not file.filename.lower().endswith(".pdf"):

        return """
        <script>
            alert("Only PDF files are allowed!");
            window.location.href="/student-dashboard";
        </script>
        """

    user_id = session["user_id"]

    filename = f"resume_{user_id}.pdf"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    try:

        # Save PDF
        file.save(filepath)

        # Read PDF
        reader = PdfReader(filepath)

        extracted_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:

                extracted_text += text + "\n"

        extracted_text = extracted_text.strip()

        if not extracted_text:

            return """
            <script>
                alert("Could not extract text from this PDF. Please upload a text-based PDF.");
                window.location.href="/student-dashboard";
            </script>
            """

        # NLP skill extraction
        detected_skills = extract_skills(
            extracted_text
        )

        # AI score
        score = calculate_skill_score(
            detected_skills
        )

        # Skill gaps
        skill_gaps = calculate_skill_gaps(
            detected_skills
        )

        connection = get_db_connection()

        if connection is None:

            return """
            <script>
                alert("Database connection failed!");
                window.location.href="/student-dashboard";
            </script>
            """

        cursor = connection.cursor()

        # Remove old analysis
        cursor.execute("""
            DELETE FROM student_resumes
            WHERE user_id = %s
        """, (user_id,))

        cursor.execute("""
            DELETE FROM student_skills
            WHERE user_id = %s
        """, (user_id,))

        # Save resume analysis
        cursor.execute("""
            INSERT INTO student_resumes
            (
                user_id,
                filename,
                resume_text,
                extracted_skills,
                skill_score
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            filename,
            extracted_text,
            ", ".join(detected_skills),
            score
        ))

        # Save detected skills
        for skill in detected_skills:

            level = calculate_skill_level(
                skill,
                extracted_text
            )

            cursor.execute("""
                INSERT INTO student_skills
                (
                    user_id,
                    skill_name,
                    skill_level
                )
                VALUES (%s, %s, %s)
            """, (
                user_id,
                skill,
                level
            ))

        connection.commit()

        cursor.close()
        connection.close()

        print("\n================================")
        print("AI / NLP RESUME ANALYSIS")
        print("================================")
        print("Detected Skills:", detected_skills)
        print("Skill Score:", score)
        print("Skill Gaps:", skill_gaps)
        print("================================\n")

        return """
        <script>
            alert("Resume uploaded successfully! AI/NLP analysis completed.");
            window.location.href="/student-dashboard";
        </script>
        """

    except Exception as e:

        print("Resume processing error:", e)

        return """
        <script>
            alert("Unable to process the resume.");
            window.location.href="/student-dashboard";
        </script>
        """


# =========================================================
# AI ANALYSIS API
# =========================================================

@app.route("/api/resume-analysis")
def resume_analysis_api():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required"
        }), 401

    data = get_student_data(
        session["user_id"]
    )

    skill_gaps = calculate_skill_gaps(
        data["skills"]
    )

    opportunities = calculate_opportunities(
        data["skills"]
    )

    return jsonify({

        "success": True,

        "skills": data["skills"],

        "skill_score": data["score"],

        "skill_gaps": skill_gaps,

        "opportunities": opportunities
    })


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return """
    <script>
        alert("Maximum resume size is 5 MB.");
        window.location.href="/student-dashboard";
    </script>
    """


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    create_tables()

    print(
        "SkillBridge AI/NLP Platform running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    app.run(debug=True)