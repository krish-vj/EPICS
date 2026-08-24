from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'doctor', 'patient'
    created_at = Column(DateTime, default=datetime.utcnow)

    doctor_profile = relationship("DoctorProfile", back_populates="user", uselist=False)
    patient_appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialisation = Column(String, index=True, nullable=False)
    working_hours = Column(JSON, nullable=False)  
    slot_duration_mins = Column(Integer, default=30, nullable=False)
    leave_days = Column(JSON, default=list, nullable=False)  

    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="booked", nullable=False)  
    symptoms = Column(Text, nullable=True)
    pre_visit_summary = Column(JSON, nullable=True)  
    post_visit_notes = Column(Text, nullable=True)
    post_visit_summary = Column(Text, nullable=True)
    google_calendar_event_id = Column(String, nullable=True)

    patient = relationship("User", back_populates="patient_appointments", foreign_keys=[patient_id])
    doctor = relationship("DoctorProfile", back_populates="appointments")
    prescription = relationship("Prescription", back_populates="appointment", uselist=False)

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True, nullable=False)
    medications = Column(JSON, nullable=False)  
    next_follow_up_date = Column(Date, nullable=True)

    appointment = relationship("Prescription", back_populates="prescription")
