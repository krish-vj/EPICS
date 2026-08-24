# Healthcare Appointment & Follow-up Manager

A production-grade, full-stack healthcare platform built with **FastAPI** (Python) and **React** (Vite + Tailwind CSS). The system goes beyond basic scheduling by integrating real-time symptom analysis with Google Gemini LLMs, Google Calendar & Workspace event synchronisation, role-based access control (RBAC), and email notification retries.

---

## 🚀 Key Features

* **Role-Based Portals (Admin, Doctor, Patient):** Secure JWT-based authentication with distinct user roles and workflows.
* **AI-Powered Pre-Visit Summaries:** Patients submit symptoms prior to booking; Google Gemini evaluates urgency levels, extracts chief complaints, and generates recommended questions for the physician.
* **Concurrency Control & Double-Booking Prevention:** Implements database row-level locking (`SELECT ... FOR UPDATE`) to guarantee transaction safety during simultaneous booking attempts.
* **Doctor Leave Conflict Management:** Admin profile controls for working hours, slot durations, and vacation/leave days[cite: 5, 9].
* **Post-Visit Clinical Flow & Summaries:** Doctors submit consultation notes and prescriptions, triggering a second Gemini pipeline to generate an easy-to-read, patient-friendly medical summary[cite: 8, 13].
* **Notifications & Calendar Sync:** SMTP email dispatch with exponential backoff retry mechanisms and Google Calendar event lifecycles[cite: 11, 12].

---

## 📂 Project Structure

```text
healthcare_manager_fullstack/
├── backend/
│   ├── app/
│   │   ├── routers/        # Auth, Admin, Doctor, and Patient endpoints
│   │   ├── services/       # Google Gemini, Calendar, and Mail integrations
│   │   ├── database.py     # SQLAlchemy session setup
│   │   ├── models.py       # DB Schemas (User, DoctorProfile, Appointment, Prescription)
│   │   ├── schemas.py      # Pydantic validation models
│   │   └── main.py         # FastAPI application entry point
│   ├── .env.example        # Environment variable template
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── src/
    │   ├── services/       # Axios API client & endpoints mapping
    │   ├── App.jsx         # Multi-portal UI views
    │   └── index.css       # Tailwind CSS styles
    ├── package.json        # Node.js dependencies
    └── vite.config.js      # Vite configuration