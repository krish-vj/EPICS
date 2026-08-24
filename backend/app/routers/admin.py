from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DoctorProfile
from app.schemas import DoctorProfileCreate, DoctorProfileResponse, LeaveUpdate
from app.routers.auth import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix="/admin", tags=["Admin Portal"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/doctors", response_model=DoctorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_doctor_profile(profile_in: DoctorProfileCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == profile_in.user_id, User.role == "doctor").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or is not designated as a doctor")
    
    existing_profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == profile_in.user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Doctor profile already exists for this user")

    new_profile = DoctorProfile(
        user_id=profile_in.user_id,
        specialisation=profile_in.specialisation,
        working_hours=profile_in.working_hours,
        slot_duration_mins=profile_in.slot_duration_mins,
        leave_days=profile_in.leave_days
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.put("/doctors/{doctor_id}/leave", response_model=DoctorProfileResponse)
def update_doctor_leave(doctor_id: int, leave_in: LeaveUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    doctor.leave_days = leave_in.leave_days
    db.commit()
    db.refresh(doctor)
    return doctor
