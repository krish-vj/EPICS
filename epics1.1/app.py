from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import db
from models import User, Patient, Doctor, DiseaseCase

app = Flask(__name__)
app.secret_key = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://pyuser:pyuser123@localhost/medical_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()
from models import User

with app.app_context():
    if not User.query.filter_by(role="ADMIN").first():
        admin = User(
            email="admin",
            password="admin",
            role="ADMIN"
        )
        db.session.add(admin)
        db.session.commit()
        print("ADMIN CREATED: admin@platform.com / admin")


# ---------------- AUTH ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            email=request.form["email"],
            password=request.form["password"]
        ).first()
        if user:
            login_user(user)
            if user.role == "PATIENT":
                return redirect("/patient")
            if user.role == "DOCTOR":
                return redirect("/doctor")
            if user.role == "ADMIN":
                return redirect("/admin")
    return render_template("login.html")

# ---------------- REGISTER ----------------

@app.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        user = User(
            email=request.form["email"],
            password=request.form["password"],
            role="PATIENT"
        )
        db.session.add(user)
        db.session.commit()

        patient = Patient(
            user_id=user.id,
            name=request.form["name"],
            age=request.form["age"],
            gender=request.form["gender"],
            blood_group=request.form["blood_group"],
            medical_history=request.form["history"]
        )
        db.session.add(patient)
        db.session.commit()
        return redirect("/")
    return render_template("register_patient.html")

@app.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        user = User(
            email=request.form["email"],
            password=request.form["password"],
            role="DOCTOR"
        )
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(
            user_id=user.id,
            name=request.form["name"],
            specialization=request.form["specialization"]
        )
        db.session.add(doctor)
        db.session.commit()
        return redirect("/")
    return render_template("register_doctor.html")

# ---------------- PATIENT ----------------

@app.route("/patient", methods=["GET", "POST"])
@login_required
def patient_dashboard():
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        case = DiseaseCase(
            patient_id=patient.id,
            symptoms=request.form["symptoms"]
        )
        db.session.add(case)
        db.session.commit()

    cases = DiseaseCase.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_dashboard.html", cases=cases)

# ---------------- DOCTOR ----------------

@app.route("/doctor")
@login_required
def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor.approved:
        return "Waiting for admin approval"

    cases = DiseaseCase.query.all()
    enriched = []
    for c in cases:
        patient = Patient.query.get(c.patient_id)
        enriched.append((c, patient))

    return render_template("doctor_dashboard.html", cases=enriched)

# ---------------- ADMIN ----------------

@app.route("/admin")
@login_required
def admin_dashboard():
    doctors = Doctor.query.filter_by(approved=False).all()
    return render_template("admin_dashboard.html", doctors=doctors)

@app.route("/approve/<doctor_id>")
@login_required
def approve_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    doctor.approved = True
    db.session.commit()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)

