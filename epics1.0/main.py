"""
FastAPI Main Application
Healthcare Management System Backend
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

from config import settings
from models import get_db, create_tables, User, Doctor, Patient, Appointment, Prescription, LabTest, Review, Department, DoctorAvailability
from schemas import (
    UserCreate, UserResponse, UserUpdate,
    DoctorCreate, DoctorResponse, DoctorUpdate,
    PatientCreate, PatientResponse, PatientUpdate,
    AppointmentCreate, AppointmentResponse, AppointmentUpdate,
    PrescriptionCreate, PrescriptionResponse,
    LabTestCreate, LabTestResponse, LabTestUpdate,
    ReviewCreate, ReviewResponse,
    DepartmentCreate, DepartmentResponse,
    AvailabilityCreate, AvailabilityResponse,
    LoginRequest, Token, SuccessResponse
)
from auth import (
    PasswordHandler, TokenHandler, authenticate_user,
    get_current_user, get_current_admin, get_current_doctor, get_current_patient
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Healthcare Management System API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],   # VERY IMPORTANT
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# ============= Authentication Endpoints =============

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = PasswordHandler.hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        user_type=user_data.user_type,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
        address=user_data.address,
        city=user_data.city,
        state=user_data.state,
        zip_code=user_data.zip_code,
        country=user_data.country
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(credentials.email, credentials.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = TokenHandler.create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "user_type": user.user_type
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ============= User Endpoints =============

@app.get("/api/v1/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    query = db.query(User)
    if user_type:
        query = query.filter(User.user_type == user_type)
    users = query.offset(skip).limit(limit).all()
    return users


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    # Users can only view their own profile unless they're admin
    if current_user.user_type != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.put("/api/v1/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information"""
    # Users can only update their own profile unless they're admin
    if current_user.user_type != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


# ============= Doctor Endpoints =============

@app.post("/api/v1/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: DoctorCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new doctor (Admin only)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == doctor_data.user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = PasswordHandler.hash_password(doctor_data.user.password)
    new_user = User(
        email=doctor_data.user.email,
        password_hash=hashed_password,
        user_type="doctor",
        first_name=doctor_data.user.first_name,
        last_name=doctor_data.user.last_name,
        phone=doctor_data.user.phone,
        date_of_birth=doctor_data.user.date_of_birth,
        gender=doctor_data.user.gender,
        address=doctor_data.user.address,
        city=doctor_data.user.city,
        state=doctor_data.user.state,
        zip_code=doctor_data.user.zip_code,
        country=doctor_data.user.country
    )
    db.add(new_user)
    db.flush()
    
    # Create doctor
    new_doctor = Doctor(
        user_id=new_user.id,
        specialization=doctor_data.specialization,
        license_number=doctor_data.license_number,
        qualification=doctor_data.qualification,
        years_of_experience=doctor_data.years_of_experience,
        consultation_fee=doctor_data.consultation_fee,
        bio=doctor_data.bio,
        hospital_affiliation=doctor_data.hospital_affiliation,
        available_for_consultation=doctor_data.available_for_consultation
    )
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return new_doctor


@app.get("/api/v1/doctors", response_model=List[DoctorResponse])
async def get_doctors(
    skip: int = 0,
    limit: int = 100,
    specialization: Optional[str] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all doctors"""
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization.contains(specialization))
    if available is not None:
        query = query.filter(Doctor.available_for_consultation == available)
    doctors = query.offset(skip).limit(limit).all()
    return doctors


@app.get("/api/v1/doctors/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get doctor by ID"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return doctor


@app.put("/api/v1/doctors/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_update: DoctorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update doctor information"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check authorization
    if current_user.user_type != "admin" and doctor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this doctor"
        )
    
    # Update fields
    for field, value in doctor_update.dict(exclude_unset=True).items():
        setattr(doctor, field, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor


# ============= Patient Endpoints =============

@app.post("/api/v1/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient (public registration)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == patient_data.user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = PasswordHandler.hash_password(patient_data.user.password)
    new_user = User(
        email=patient_data.user.email,
        password_hash=hashed_password,
        user_type="patient",
        first_name=patient_data.user.first_name,
        last_name=patient_data.user.last_name,
        phone=patient_data.user.phone,
        date_of_birth=patient_data.user.date_of_birth,
        gender=patient_data.user.gender,
        address=patient_data.user.address,
        city=patient_data.user.city,
        state=patient_data.user.state,
        zip_code=patient_data.user.zip_code,
        country=patient_data.user.country
    )
    db.add(new_user)
    db.flush()
    
    # Create patient
    new_patient = Patient(
        user_id=new_user.id,
        blood_group=patient_data.blood_group,
        height_cm=patient_data.height_cm,
        weight_kg=patient_data.weight_kg,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        emergency_contact_relation=patient_data.emergency_contact_relation,
        medical_history=patient_data.medical_history,
        allergies=patient_data.allergies,
        current_medications=patient_data.current_medications,
        insurance_provider=patient_data.insurance_provider,
        insurance_policy_number=patient_data.insurance_policy_number
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return new_patient


@app.get("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient by ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check authorization
    if current_user.user_type not in ["admin", "doctor"] and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this patient"
        )
    
    return patient


@app.put("/api/v1/patients/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update patient information"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check authorization
    if current_user.user_type != "admin" and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this patient"
        )
    
    # Update fields
    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    return patient


# ============= Appointment Endpoints =============

@app.post("/api/v1/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    # Get patient record
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appointment_data.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Create appointment
    new_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appointment_data.doctor_id,
        appointment_date=appointment_data.appointment_date,
        appointment_time=appointment_data.appointment_time,
        appointment_type=appointment_data.appointment_type,
        reason_for_visit=appointment_data.reason_for_visit,
        symptoms=appointment_data.symptoms,
        consultation_fee=doctor.consultation_fee
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@app.get("/api/v1/appointments", response_model=List[AppointmentResponse])
async def get_appointments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointments (filtered by user role)"""
    query = db.query(Appointment)
    
    if current_user.user_type == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
    elif current_user.user_type == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if doctor:
            query = query.filter(Appointment.doctor_id == doctor.id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.offset(skip).limit(limit).all()
    return appointments


@app.get("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointment by ID"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check authorization
    if current_user.user_type == "patient":
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    elif current_user.user_type == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or appointment.doctor_id != doctor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return appointment


@app.put("/api/v1/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Update fields
    for field, value in appointment_update.dict(exclude_unset=True).items():
        setattr(appointment, field, value)
    
    db.commit()
    db.refresh(appointment)
    return appointment


# ============= Health Check =============

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Management System API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
