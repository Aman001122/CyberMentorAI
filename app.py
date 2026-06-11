from flask import Flask, render_template, request, redirect
from services.openrouter_service import analyze_threat
from models.analysis import Analysis
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from models.user import db, User


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cybermentor.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "cybermentor"

db.init_app(app)




@app.route("/history")
@login_required
def history():
    analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "history.html",
        analyses=analyses
    )


@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    result = None

    if request.method == "POST":
        incident = request.form["incident"]

        result = analyze_threat(incident)

        analysis = Analysis(
            user_id=current_user.id,
            incident_text=incident,
            result=result
        )

        db.session.add(analysis)
        db.session.commit()

    return render_template(
        "analyze.html",
        result=result
    )

@app.route("/dashboard")
@login_required
def dashboard():

    analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).all()

    total_analyses = len(analyses)

    highest_risk = 0

    recent_threat = "None"

    for analysis in analyses:

        if "Risk Score:" in analysis.result:

            try:
                score = int(
                    analysis.result.split("Risk Score: ")[1]
                    .split("/100")[0]
                )

                if score > highest_risk:
                    highest_risk = score

            except:
                pass

    if analyses:

        latest_analysis = analyses[-1]

        if "Threat Type:" in latest_analysis.result:

            try:

                recent_threat = (
                    latest_analysis.result
                    .split("Threat Type:")[1]
                    .split("Risk Level:")[0]
                    .strip()
                )

            except:
                pass

    return render_template(
        "dashboard.html",
        username=current_user.username,
        total_analyses=total_analyses,
        highest_risk=highest_risk,
        recent_threat=recent_threat
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already exists"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()