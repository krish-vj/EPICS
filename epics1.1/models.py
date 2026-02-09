from db import db
from flask_login import UserMixin
from datetime import datetime
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20))  # PATIENT, DOCTOR, ADMIN

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(10))
    medical_history = db.Column(db.Text)

class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)

class DiseaseCase(db.Model):
    __tablename__ = "disease_cases"
    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey("patients.id"))
    symptoms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


