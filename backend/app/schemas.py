from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DoctorProfileCreate(BaseModel):
    user_id: int
    specialisation: str
    working_hours: Dict[str, str]
    slot_duration_mins: Optional[int] = 30
    leave_days: Optional[List[str]] = []

class DoctorProfileResponse(BaseModel):
    id: int
    user_id: int
    specialisation: str
    working_hours: Dict[str, str]
    slot_duration_mins: int
    leave_days: List[str]
    user: UserResponse

    class Config:
        from_attributes = True

class LeaveUpdate(BaseModel):
    leave_days: List[str]

class AppointmentCreate(BaseModel):
    doctor_id: int
    start_time: datetime
    symptoms: str

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    status: str
    symptoms: Optional[str] = None
    pre_visit_summary: Optional[Dict[str, Any]] = None
    post_visit_notes: Optional[str] = None
    post_visit_summary: Optional[str] = None
    google_calendar_event_id: Optional[str] = None

    class Config:
        from_attributes = True

class MedicationItem(BaseModel):
    name: str
    dosage: str
    frequency: str

class PostVisitSubmit(BaseModel):
    post_visit_notes: str
    medications: List[MedicationItem]
    next_follow_up_date: Optional[date] = None
