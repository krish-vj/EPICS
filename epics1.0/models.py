"""
SQLAlchemy Database Models
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Time, DateTime, Boolean, Enum, ForeignKey, Index, UniqueConstraint, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from config import db_config

# Create database engine
engine = create_engine(
    db_config.DATABASE_URL,
    pool_size=db_config.POOL_SIZE,
    max_overflow=db_config.MAX_OVERFLOW,
    pool_timeout=db_config.POOL_TIMEOUT,
    pool_recycle=db_config.POOL_RECYCLE,
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database session dependency
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum('patient', 'doctor', 'admin', 'staff'), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(Enum('male', 'female', 'other', 'prefer_not_to_say'))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100), default='India')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")


class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    specialization = Column(String(200), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=False)
    qualification = Column(String(500))
    years_of_experience = Column(Integer)
    consultation_fee = Column(Numeric(10, 2))
    bio = Column(Text)
    hospital_affiliation = Column(String(255))
    available_for_consultation = Column(Boolean, default=True)
    average_rating = Column(Numeric(3, 2), default=0.00, index=True)
    total_reviews = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="doctor")
    availability = relationship("DoctorAvailability", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")
    lab_tests = relationship("LabTest", back_populates="doctor")
    reviews = relationship("Review", back_populates="doctor")
    departments = relationship("DoctorDepartment", back_populates="doctor")


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="availability")
    
    __table_args__ = (
        Index('idx_doctor_day', 'doctor_id', 'day_of_week'),
    )


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    blood_group = Column(Enum('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'))
    height_cm = Column(Numeric(5, 2))
    weight_kg = Column(Numeric(5, 2))
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relation = Column(String(100))
    medical_history = Column(Text)
    allergies = Column(Text)
    current_medications = Column(Text)
    insurance_provider = Column(String(255))
    insurance_policy_number = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    lab_tests = relationship("LabTest", back_populates="patient")
    reviews = relationship("Review", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    appointment_type = Column(Enum('consultation', 'follow_up', 'emergency', 'checkup'), nullable=False)
    status = Column(Enum('scheduled', 'confirmed', 'cancelled', 'completed', 'no_show'), default='scheduled', index=True)
    reason_for_visit = Column(Text)
    symptoms = Column(Text)
    diagnosis = Column(Text)
    prescription = Column(Text)
    notes = Column(Text)
    consultation_fee = Column(Numeric(10, 2))
    payment_status = Column(Enum('pending', 'paid', 'refunded'), default='pending')
    cancelled_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    cancellation_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    medical_records = relationship("MedicalRecord", back_populates="appointment")
    prescriptions = relationship("Prescription", back_populates="appointment")
    lab_tests = relationship("LabTest", back_populates="appointment")
    reviews = relationship("Review", back_populates="appointment")
    
    __table_args__ = (
        Index('idx_patient_appointments', 'patient_id', 'appointment_date'),
        Index('idx_doctor_appointments', 'doctor_id', 'appointment_date'),
    )


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='SET NULL'))
    record_date = Column(Date, nullable=False)
    record_type = Column(Enum('diagnosis', 'prescription', 'lab_result', 'imaging', 'surgery', 'vaccination', 'other'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_url = Column(String(500))
    file_type = Column(String(50))
    is_confidential = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("Doctor", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    
    __table_args__ = (
        Index('idx_patient_records', 'patient_id', 'record_date'),
    )


class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='SET NULL'))
    prescription_date = Column(Date, nullable=False)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(100))
    instructions = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    appointment = relationship("Appointment", back_populates="prescriptions")
    
    __table_args__ = (
        Index('idx_patient_prescriptions', 'patient_id', 'is_active'),
    )


class LabTest(Base):
    __tablename__ = "lab_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='SET NULL'))
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(100))
    test_date = Column(Date, nullable=False)
    result_date = Column(Date)
    status = Column(Enum('ordered', 'sample_collected', 'in_progress', 'completed', 'cancelled'), default='ordered', index=True)
    result_value = Column(String(255))
    normal_range = Column(String(255))
    unit = Column(String(50))
    remarks = Column(Text)
    lab_technician = Column(String(200))
    file_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="lab_tests")
    doctor = relationship("Doctor", back_populates="lab_tests")
    appointment = relationship("Appointment", back_populates="lab_tests")
    
    __table_args__ = (
        Index('idx_patient_tests', 'patient_id', 'test_date'),
    )


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id', ondelete='SET NULL'))
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="reviews")
    doctor = relationship("Doctor", back_populates="reviews")
    appointment = relationship("Appointment", back_populates="reviews")
    
    __table_args__ = (
        UniqueConstraint('patient_id', 'appointment_id', name='unique_patient_appointment_review'),
        Index('idx_doctor_reviews', 'doctor_id', 'rating'),
    )


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    notification_type = Column(Enum('appointment', 'prescription', 'lab_result', 'review', 'reminder', 'system'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_user_notifications', 'user_id', 'is_read', 'created_at'),
    )


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    head_doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='SET NULL'))
    location = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctors = relationship("DoctorDepartment", back_populates="department")


class DoctorDepartment(Base):
    __tablename__ = "doctor_departments"
    
    doctor_id = Column(Integer, ForeignKey('doctors.id', ondelete='CASCADE'), primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='CASCADE'), primary_key=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="departments")
    department = relationship("Department", back_populates="doctors")


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")