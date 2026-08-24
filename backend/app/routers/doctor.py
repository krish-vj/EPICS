from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, DoctorProfile, Appointment, Prescription
from app.schemas import AppointmentResponse, PostVisitSubmit
from app.routers.auth import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.services.llm_service import generate_post_visit_summary

router = APIRouter(prefix="/doctor", tags=["Doctor Portal"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_doctor(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> tuple[User, DoctorProfile]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "doctor":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.doctor_profile:
        raise credentials_exception
    return user, user.doctor_profile

@router.get("/appointments", response_model=List[AppointmentResponse])
def get_doctor_appointments(db: Session = Depends(get_db), doc_data: tuple[User, DoctorProfile] = Depends(get_current_doctor)):
    _, doctor_profile = doc_data
    appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor_profile.id).all()
    return appointments

@router.post("/appointments/{appointment_id}/complete")
def submit_visit_notes(
    appointment_id: int, 
    post_visit_in: PostVisitSubmit, 
    db: Session = Depends(get_db), 
    doc_data: tuple[User, DoctorProfile] = Depends(get_current_doctor)
):
    _, doctor_profile = doc_data
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id, 
        Appointment.doctor_id == doctor_profile.id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    summary_text = generate_post_visit_summary(post_visit_in.post_visit_notes)

    appointment.post_visit_notes = post_visit_in.post_visit_notes
    appointment.post_visit_summary = summary_text
    appointment.status = "completed"

    prescription = Prescription(
        appointment_id=appointment.id,
        medications=[m.model_dump() for m in post_visit_in.medications],
        next_follow_up_date=post_visit_in.next_follow_up_date
    )
    db.add(prescription)
    db.commit()

    return {
        "message": "Post-visit notes submitted successfully",
        "post_visit_summary": summary_text
    }
