"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum


# Enums
class UserType(str, Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"
    staff = "staff"


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class AppointmentType(str, Enum):
    consultation = "consultation"
    follow_up = "follow_up"
    emergency = "emergency"
    checkup = "checkup"


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    refunded = "refunded"


class DayOfWeek(str, Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    user_type: UserType
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "India"


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Doctor Schemas
class DoctorBase(BaseModel):
    specialization: str
    license_number: str
    qualification: Optional[str] = None
    years_of_experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    hospital_affiliation: Optional[str] = None
    available_for_consultation: bool = True


class DoctorCreate(DoctorBase):
    user: UserCreate


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    years_of_experience: Optional[int] = None
    consultation_fee: Optional[float] = None
    bio: Optional[str] = None
    hospital_affiliation: Optional[str] = None
    available_for_consultation: Optional[bool] = None


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    average_rating: float
    total_reviews: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True


# Doctor Availability Schemas
class AvailabilityBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    is_available: bool = True


class AvailabilityCreate(AvailabilityBase):
    doctor_id: int


class AvailabilityResponse(AvailabilityBase):
    id: int
    doctor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Patient Schemas
class PatientBase(BaseModel):
    blood_group: Optional[BloodGroup] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None


class PatientCreate(PatientBase):
    user: UserCreate


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True


# Appointment Schemas
class AppointmentBase(BaseModel):
    appointment_date: date
    appointment_time: time
    appointment_type: AppointmentType
    reason_for_visit: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    doctor_id: int


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    status: Optional[AppointmentStatus] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    notes: Optional[str] = None
    payment_status: Optional[PaymentStatus] = None


class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    status: AppointmentStatus
    consultation_fee: Optional[float]
    payment_status: PaymentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# Prescription Schemas
class PrescriptionBase(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: Optional[str] = None
    instructions: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    patient_id: int
    appointment_id: Optional[int] = None
    prescription_date: date


class PrescriptionResponse(PrescriptionBase):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    prescription_date: date
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Lab Test Schemas
class LabTestBase(BaseModel):
    test_name: str
    test_type: Optional[str] = None
    test_date: date


class LabTestCreate(LabTestBase):
    patient_id: int
    appointment_id: Optional[int] = None


class LabTestUpdate(BaseModel):
    result_date: Optional[date] = None
    status: Optional[str] = None
    result_value: Optional[str] = None
    normal_range: Optional[str] = None
    unit: Optional[str] = None
    remarks: Optional[str] = None
    lab_technician: Optional[str] = None


class LabTestResponse(LabTestBase):
    id: int
    patient_id: int
    doctor_id: int
    result_date: Optional[date]
    status: str
    result_value: Optional[str]
    normal_range: Optional[str]
    unit: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Review Schemas
class ReviewBase(BaseModel):
    rating: int
    review_text: Optional[str] = None
    is_anonymous: bool = False
    
    @validator('rating')
    def rating_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewCreate(ReviewBase):
    doctor_id: int
    appointment_id: Optional[int] = None


class ReviewResponse(ReviewBase):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class DepartmentCreate(DepartmentBase):
    head_doctor_id: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    id: int
    head_doctor_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Login/Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    email: str
    user_type: UserType


# Response Models
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[dict] = None
