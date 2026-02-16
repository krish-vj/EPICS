from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import db
from models import User, Patient, Doctor, DiseaseCase
import os

app = Flask(__name__)
app.secret_key = "highly_secure_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///medical_platform.db" # Using SQLite for easier setup
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Initialize DB and Admin
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin").first():
        admin = User(email="admin", password="admin", role="ADMIN")
        db.session.add(admin)
        db.session.commit()

# --- AUTH ROUTES ---

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for(f"{user.role.lower()}_dashboard"))
        flash("Invalid Credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        
        if User.query.filter_by(email=email).first():
            return "Email already exists"

        user = User(email=email, password=password, role=role.upper())
        db.session.add(user)
        db.session.commit()

        if role.upper() == "PATIENT":
            patient = Patient(user_id=user.id, name=name, age=request.form.get("age"), 
                              history=request.form.get("medical_history"))
            db.session.add(patient)

    db.session.add(patient)
        else:
            doctor = Doctor(user_id=user.id, name=name, spec=request.form.get("specialization"))
            db.session.add(doctor)
        
        db.session.commit()
        return redirect(url_for("login"))
    return render_template(f"register_{role}.html")

# --- PATIENT LOGIC ---

@app.route("/patient", methods=["GET", "POST"])
@login_required
def patient_dashboard():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if request.method == "POST":
        # Check if updating history or opening case
        if "update_history" in request.form:
            patient.medical_history = request.form.get("history")
        else:
            new_case = DiseaseCase(patient_id=patient.id, symptoms=request.form.get("symptoms"))
            db.session.add(new_case)
        db.session.commit()
    
    cases = DiseaseCase.query.filter_by(patient_id=patient.id).all()
    return render_template("patient_dashboard.html", patient=patient, cases=cases)

# --- DOCTOR LOGIC ---

@app.route("/doctor")
@login_required
def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor.approved:
        return "<h1>Account Pending Admin Approval</h1><a href='/logout'>Logout</a>"
    
    # Cases not yet taken by anyone
    available_cases = DiseaseCase.query.filter_by(doctor_id=None).all()
    # Cases taken by THIS doctor
    my_patients = DiseaseCase.query.filter_by(doctor_id=doctor.id).all()
    
    return render_template("doctor_dashboard.html", available=available_cases, my_patients=my_patients)

@app.route("/claim_case/<case_id>")
@login_required
def claim_case(case_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    case = DiseaseCase.query.get(case_id)
    case.doctor_id = doctor.id
    db.session.commit()
    return redirect(url_for("doctor_dashboard"))

@app.route("/view_case/<case_id>")
@login_required
def view_case(case_id):
    case = DiseaseCase.query.get(case_id)
    patient = Patient.query.get(case.patient_id)
    return render_template("view_case.html", case=case, patient=patient)

# --- ADMIN LOGIC ---

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "ADMIN": return "Access Denied"
    pending = Doctor.query.filter_by(approved=False).all()
    return render_template("admin_dashboard.html", doctors=pending)

@app.route("/approve/<doctor_id>")
@login_required
def approve_doctor(doctor_id):
    doc = Doctor.query.get(doctor_id)
    doc.approved = True
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

# --- VIDEO CALL ---
@app.route("/call/<room_id>")
@login_required
def call(room_id):
    return render_template("video_call.html", room_id=room_id)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
