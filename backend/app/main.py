from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, admin, doctor, patient

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Appointment & Follow-up Manager",
    description="Backend API with role-based auth, LLM summaries, Google Calendar, and conflict management.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(doctor.router)
app.include_router(patient.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Healthcare Appointment & Follow-up Manager API",
        "docs_url": "/docs"
    }
