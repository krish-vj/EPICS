from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

def gen_uuid():
    return str(uuid.uuid4())

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))  # 'admin', 'doctor', 'patient'
    
    # Relationships
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False)
    doctor_profile = db.relationship('DoctorProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    medical_history = db.Column(db.Text) # Persistent history (e.g., "Diabetic, Allergies")
    
    cases = db.relationship('Case', backref='patient_profile', lazy=True)

class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    specialization = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    
    cases = db.relationship('Case', backref='doctor_profile', lazy=True)

class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    patient_profile_id = db.Column(db.Integer, db.ForeignKey('patient_profiles.id'))
    doctor_profile_id = db.Column(db.Integer, db.ForeignKey('doctor_profiles.id'), nullable=True)
    
    symptoms = db.Column(db.Text) # Current issue
    status = db.Column(db.String(20), default='open') # 'open', 'active', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
