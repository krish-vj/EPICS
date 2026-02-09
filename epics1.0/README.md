# Healthcare Management System

A comprehensive healthcare management platform with **FastAPI** backend, **MySQL** relational database, and a responsive web frontend.

## 🏥 Features

### Core Functionality
- **User Management**: Multi-role system (Admin, Doctor, Patient, Staff)
- **Doctor Management**: Profiles, specializations, schedules, ratings
- **Patient Management**: Medical records, health tracking, insurance info
- **Appointment System**: Scheduling, status tracking, payment management
- **Medical Records**: Secure storage of diagnoses, imaging, lab results
- **Prescriptions**: Digital prescription management with medication tracking
- **Lab Tests**: Test ordering, tracking, and result management
- **Reviews & Ratings**: Patient feedback system for doctors
- **Department Management**: Hospital/clinic organization structure
- **Notifications**: System-wide notification management

### Technical Features
- RESTful API with FastAPI
- MySQL relational database with SQLAlchemy ORM
- JWT authentication & authorization
- Role-based access control (RBAC)
- Comprehensive data validation with Pydantic
- CORS support for cross-origin requests
- Password hashing with bcrypt
- Relationship management (one-to-many, many-to-many)
- Indexed queries for performance

## 📋 Prerequisites

- Python 3.9+
- MySQL 8.0+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd healthcare-management-system
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database

**Start MySQL service:**
```bash
# On Linux/Mac
sudo systemctl start mysql

# On Windows (if using XAMPP/WAMP)
# Start MySQL from the control panel
```

**Create the database:**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE healthcare_db;
EXIT;
```

**Import the schema:**
```bash
mysql -u root -p healthcare_db < database_schema.sql
```

### 4. Configure Environment Variables

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=healthcare_db
SECRET_KEY=your-secret-key-here
```

### 5. Initialize Database Tables

```bash
python models.py
```

### 6. Start the FastAPI Server

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python main.py
```

The API will be available at: `http://localhost:8000`

### 7. Access the Frontend

Open your browser and navigate to:
- **Web Interface**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)

## 📚 Database Schema

### Core Tables

1. **users** - Base user information
2. **doctors** - Doctor-specific data
3. **patients** - Patient-specific data
4. **appointments** - Appointment scheduling
5. **medical_records** - Patient medical history
6. **prescriptions** - Medication prescriptions
7. **lab_tests** - Laboratory test management
8. **reviews** - Doctor reviews and ratings
9. **doctor_availability** - Doctor schedule management
10. **departments** - Hospital departments
11. **doctor_departments** - Doctor-department relationships
12. **notifications** - User notifications

### Entity Relationships

```
users (1) ←→ (1) doctors
users (1) ←→ (1) patients
doctors (1) ←→ (many) appointments
patients (1) ←→ (many) appointments
doctors (1) ←→ (many) prescriptions
patients (1) ←→ (many) prescriptions
doctors (many) ←→ (many) departments
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login and get JWT token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users` | Get all users | Admin |
| GET | `/api/v1/users/{id}` | Get user by ID | Yes |
| PUT | `/api/v1/users/{id}` | Update user | Yes |

### Doctors

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/doctors` | Create doctor | Admin |
| GET | `/api/v1/doctors` | Get all doctors | No |
| GET | `/api/v1/doctors/{id}` | Get doctor by ID | No |
| PUT | `/api/v1/doctors/{id}` | Update doctor | Yes |

### Patients

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/patients` | Register patient | No |
| GET | `/api/v1/patients/{id}` | Get patient by ID | Yes |
| PUT | `/api/v1/patients/{id}` | Update patient | Yes |

### Appointments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/appointments` | Create appointment | Patient |
| GET | `/api/v1/appointments` | Get appointments | Yes |
| GET | `/api/v1/appointments/{id}` | Get appointment by ID | Yes |
| PUT | `/api/v1/appointments/{id}` | Update appointment | Yes |

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

**Example using curl:**

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use the token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

## 📝 API Usage Examples

### Register a Patient

```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "email": "patient@example.com",
      "password": "password123",
      "user_type": "patient",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+91-9876543210",
      "date_of_birth": "1990-01-01",
      "gender": "male",
      "city": "Mumbai",
      "state": "Maharashtra",
      "country": "India"
    },
    "blood_group": "O+"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "password123"
  }'
```

### Create Appointment

```bash
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "doctor_id": 1,
    "appointment_date": "2024-02-15",
    "appointment_time": "10:00:00",
    "appointment_type": "consultation",
    "reason_for_visit": "Regular checkup",
    "symptoms": "None"
  }'
```

## 🏗️ Project Structure

```
healthcare-management-system/
├── main.py                  # FastAPI application
├── models.py                # SQLAlchemy database models
├── schemas.py               # Pydantic schemas
├── auth.py                  # Authentication utilities
├── config.py                # Configuration settings
├── database_schema.sql      # MySQL database schema
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
└── static/
    └── index.html          # Web frontend
```

## 🔒 Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for different user types
- **Input Validation**: Comprehensive validation using Pydantic
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Controlled cross-origin access

## 🎯 User Roles

1. **Admin**: Full system access, can manage all users and data
2. **Doctor**: Can view patients, manage appointments, create prescriptions
3. **Patient**: Can book appointments, view own medical records
4. **Staff**: Can assist with administrative tasks

## 📱 Multi-Platform Support

The FastAPI backend is designed to work with:
- **Web Applications** (React, Vue, Angular)
- **Mobile Apps** (Android, iOS via REST API)
- **Desktop Applications**
- **Third-party integrations**

## 🧪 Testing the API

### Using FastAPI Swagger UI

Navigate to: http://localhost:8000/docs

This interactive documentation allows you to:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Authenticate and test protected endpoints

### Using curl or Postman

Import the API endpoints into Postman or use curl commands as shown in the examples above.

## 🔧 Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-restart on code changes.

### Database Migrations

To modify the database schema:

1. Update `models.py` with your changes
2. Run `python models.py` to recreate tables
3. Or use Alembic for proper migrations:

```bash
pip install alembic
alembic init alembic
# Configure alembic.ini
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🌐 Deployment

### Production Setup

1. **Update configuration:**
   - Set strong `SECRET_KEY` in `.env`
   - Use production MySQL credentials
   - Disable debug mode

2. **Use production server:**
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Setup reverse proxy (Nginx example):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u root -p -h localhost
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the code comments

## 🚀 Future Enhancements

- [ ] Add file upload for medical reports
- [ ] Implement real-time notifications (WebSocket)
- [ ] Add payment gateway integration
- [ ] Create mobile app (React Native/Flutter)
- [ ] Add video consultation feature
- [ ] Implement appointment reminders (SMS/Email)
- [ ] Add analytics dashboard
- [ ] Multi-language support
- [ ] Electronic Health Records (EHR) integration
