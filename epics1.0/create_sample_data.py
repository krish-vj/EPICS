"""
Sample Data Generator for Healthcare Management System
Run this script to populate the database with test data
"""
from datetime import datetime, date, time
from models import (
    SessionLocal, User, Doctor, Patient, Department, DoctorDepartment,
    DoctorAvailability, Appointment
)
from auth import PasswordHandler

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        print("Creating sample data...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.query(User).delete()
        # db.commit()
        
        # Create Admin User
        print("Creating admin user...")
        admin_user = User(
            email="admin@healthcare.com",
            password_hash=PasswordHandler.hash_password("admin123"),
            user_type="admin",
            first_name="System",
            last_name="Administrator",
            phone="+91-9999999999",
            gender="male",
            city="Mumbai",
            state="Maharashtra",
            country="India"
        )
        db.add(admin_user)
        db.flush()
        
        # Create Sample Doctors
        print("Creating sample doctors...")
        
        doctor_data = [
            {
                "email": "dr.sharma@healthcare.com",
                "first_name": "Rajesh",
                "last_name": "Sharma",
                "specialization": "Cardiology",
                "qualification": "MBBS, MD (Cardiology), FACC",
                "experience": 15,
                "fee": 1500.00,
                "bio": "Expert in cardiac care with 15 years of experience in treating heart diseases."
            },
            {
                "email": "dr.patel@healthcare.com",
                "first_name": "Priya",
                "last_name": "Patel",
                "specialization": "Pediatrics",
                "qualification": "MBBS, MD (Pediatrics), DCH",
                "experience": 10,
                "fee": 1000.00,
                "bio": "Specialized in child healthcare and development."
            },
            {
                "email": "dr.kumar@healthcare.com",
                "first_name": "Amit",
                "last_name": "Kumar",
                "specialization": "Orthopedics",
                "qualification": "MBBS, MS (Orthopedics)",
                "experience": 12,
                "fee": 1200.00,
                "bio": "Expert in bone, joint, and muscle care."
            },
            {
                "email": "dr.singh@healthcare.com",
                "first_name": "Anjali",
                "last_name": "Singh",
                "specialization": "Dermatology",
                "qualification": "MBBS, MD (Dermatology)",
                "experience": 8,
                "fee": 800.00,
                "bio": "Specialized in skin, hair, and nail treatments."
            },
            {
                "email": "dr.verma@healthcare.com",
                "first_name": "Vikram",
                "last_name": "Verma",
                "specialization": "General Medicine",
                "qualification": "MBBS, MD (General Medicine)",
                "experience": 20,
                "fee": 700.00,
                "bio": "General physician with extensive experience in primary care."
            }
        ]
        
        doctors = []
        for doc in doctor_data:
            # Create user for doctor
            user = User(
                email=doc["email"],
                password_hash=PasswordHandler.hash_password("doctor123"),
                user_type="doctor",
                first_name=doc["first_name"],
                last_name=doc["last_name"],
                phone="+91-98765432" + str(len(doctors)),
                gender="male" if doc["first_name"] in ["Rajesh", "Amit", "Vikram"] else "female",
                city="Mumbai",
                state="Maharashtra",
                country="India"
            )
            db.add(user)
            db.flush()
            
            # Create doctor profile
            doctor = Doctor(
                user_id=user.id,
                specialization=doc["specialization"],
                license_number=f"MH-{1000 + len(doctors)}",
                qualification=doc["qualification"],
                years_of_experience=doc["experience"],
                consultation_fee=doc["fee"],
                bio=doc["bio"],
                hospital_affiliation="City General Hospital",
                available_for_consultation=True
            )
            db.add(doctor)
            db.flush()
            doctors.append(doctor)
            
            # Add availability (Monday to Friday, 9 AM to 5 PM)
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    is_available=True
                )
                db.add(availability)
        
        # Create Sample Patients
        print("Creating sample patients...")
        
        patient_data = [
            {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "blood_group": "O+",
                "phone": "+91-9876543210"
            },
            {
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "blood_group": "A+",
                "phone": "+91-9876543211"
            },
            {
                "email": "rahul.mehta@example.com",
                "first_name": "Rahul",
                "last_name": "Mehta",
                "blood_group": "B+",
                "phone": "+91-9876543212"
            }
        ]
        
        patients = []
        for pat in patient_data:
            # Create user for patient
            user = User(
                email=pat["email"],
                password_hash=PasswordHandler.hash_password("patient123"),
                user_type="patient",
                first_name=pat["first_name"],
                last_name=pat["last_name"],
                phone=pat["phone"],
                date_of_birth=date(1990, 1, 1),
                gender="male" if pat["first_name"] in ["John", "Rahul"] else "female",
                address="123 Main Street",
                city="Mumbai",
                state="Maharashtra",
                zip_code="400001",
                country="India"
            )
            db.add(user)
            db.flush()
            
            # Create patient profile
            patient = Patient(
                user_id=user.id,
                blood_group=pat["blood_group"],
                height_cm=170.0,
                weight_kg=70.0,
                emergency_contact_name="Emergency Contact",
                emergency_contact_phone="+91-9999999999",
                emergency_contact_relation="Family"
            )
            db.add(patient)
            db.flush()
            patients.append(patient)
        
        # Create Departments
        print("Creating departments...")
        
        dept_names = ["Cardiology", "Pediatrics", "Orthopedics", "Dermatology", "General Medicine"]
        departments = []
        
        for i, dept_name in enumerate(dept_names):
            dept = Department(
                name=dept_name,
                description=f"Department of {dept_name}",
                head_doctor_id=doctors[i].id if i < len(doctors) else None,
                location=f"Building A, Floor {i+1}",
                phone="+91-2212345" + str(i),
                email=f"{dept_name.lower().replace(' ', '')}@hospital.com",
                is_active=True
            )
            db.add(dept)
            db.flush()
            departments.append(dept)
            
            # Link doctor to department
            if i < len(doctors):
                doc_dept = DoctorDepartment(
                    doctor_id=doctors[i].id,
                    department_id=dept.id,
                    is_primary=True
                )
                db.add(doc_dept)
        
        # Create Sample Appointments
        print("Creating sample appointments...")
        
        if patients and doctors:
            appointment = Appointment(
                patient_id=patients[0].id,
                doctor_id=doctors[0].id,
                appointment_date=date(2024, 2, 15),
                appointment_time=time(10, 0),
                appointment_type="consultation",
                status="scheduled",
                reason_for_visit="Regular checkup",
                symptoms="None",
                consultation_fee=doctors[0].consultation_fee,
                payment_status="pending"
            )
            db.add(appointment)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*50)
        print("✅ Sample data created successfully!")
        print("="*50)
        print("\n📝 Test Credentials:")
        print("\nAdmin:")
        print("  Email: admin@healthcare.com")
        print("  Password: admin123")
        print("\nDoctors:")
        print("  Email: dr.sharma@healthcare.com (or other doctor emails)")
        print("  Password: doctor123")
        print("\nPatients:")
        print("  Email: john.doe@example.com (or other patient emails)")
        print("  Password: patient123")
        print("\n" + "="*50)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Healthcare Management System - Sample Data Generator")
    print("="*50)
    
    response = input("\nThis will create sample data in the database. Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        create_sample_data()
    else:
        print("Operation cancelled.")
