from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from app.database import get_db
from app.models import User, DoctorProfile, Appointment
from app.schemas import AppointmentCreate, AppointmentResponse, DoctorProfileResponse
from app.routers.auth import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.services.llm_service import generate_pre_visit_summary
from app.services.google_mail import send_email_with_retry

router = APIRouter(prefix="/patient", tags=["Patient Portal"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_patient(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "patient":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/doctors", response_model=List[DoctorProfileResponse])
def search_doctors(specialisation: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(DoctorProfile)
    if specialisation:
        query = query.filter(DoctorProfile.specialisation.ilike(f"%{specialisation}%"))
    return query.all()

@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    appointment_in: AppointmentCreate, 
    db: Session = Depends(get_db), 
    patient: User = Depends(get_current_patient)
):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == appointment_in.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    date_str = appointment_in.start_time.strftime("%Y-%m-%d")
    if date_str in doctor.leave_days:
        raise HTTPException(status_code=400, detail="Doctor is on leave on this date")

    end_time = appointment_in.start_time + timedelta(minutes=doctor.slot_duration_mins)

    existing_conflict = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status == "booked",
        Appointment.start_time < end_time,
        Appointment.end_time > appointment_in.start_time
    ).with_for_update().first()

    if existing_conflict:
        raise HTTPException(status_code=409, detail="This time slot is already booked. Please choose another.")

    pre_summary = generate_pre_visit_summary(appointment_in.symptoms)

    new_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        start_time=appointment_in.start_time,
        end_time=end_time,
        status="booked",
        symptoms=appointment_in.symptoms,
        pre_visit_summary=pre_summary
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    send_email_with_retry(
        to_email=patient.email,
        subject="Appointment Booking Confirmation",
        body=f"Hello {patient.name},\n\nYour appointment with Doctor ID {doctor.id} is confirmed for {appointment_in.start_time}.\nUrgency: {pre_summary.get('urgency')}\n\nThank you!"
    )

    return new_appointment
