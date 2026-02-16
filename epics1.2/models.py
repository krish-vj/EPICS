from db import db
from flask_login import UserMixin
import uuid

def gen_id(): return str(uuid.uuid4())

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20)) # ADMIN, DOCTOR, PATIENT

class Patient(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    medical_history = db.Column(db.Text)

class Doctor(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    spec = db.Column(db.String(100))
    approved = db.Column(db.Boolean, default=False)

class DiseaseCase(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=gen_id)
    patient_id = db.Column(db.String(36), db.ForeignKey('patient.id'))
    doctor_id = db.Column(db.String(36), db.ForeignKey('doctor.id'), nullable=True)
    symptoms = db.Column(db.Text)
    patient = db.relationship('Patient', backref='cases')
