# Implementation Roadmap: EPICS Telehealth

This document outlines the step-by-step plan to evolve the current prototype into the full vision described in `goal.md`.

## Phase 1: Core Foundation & Data Richness (Current Focus)
*Goal: Move beyond basic profiles to clinical-grade data collection.*

1.  **Enhance Medical Data Models:**
    *   Update `Case` and `PatientProfile` to include structured vitals (BP, Heart Rate, SpO2, Temperature).
    *   Add geographical metadata (latitude/longitude) and "Budget/Insurance" fields to user profiles.
2.  **Medical Report Management:**
    *   Implement secure file uploads for PDF/Image reports (Blood tests, X-rays).
    *   Ensure all doctors assigned to a case can view these reports.
3.  **Basic Case Workflow:**
    *   Allow "Village Doctors" to open cases on behalf of patients.
    *   Implement case assignment/handoff logic between generalists and specialists.

## Phase 2: Intelligent Recommendations (LLM Integration)
*Goal: Automate the specialist matching process.*

1.  **LLM Integration (Gemini API):**
    *   Build a service that takes symptoms, vitals, and medical history as input.
    *   Output: Recommended specialist type (e.g., "Cardiologist", "Neurologist") with reasoning.
2.  **Search & Discovery Algorithm:**
    *   Implement a search filter for doctors based on geographical proximity, specialization, and "Budget Compatibility" (Insurance vs. Cash).
3.  **Allergy & Conflict Warning System:**
    *   Implement a "Safety Check" that triggers when a doctor prescribes medicine, cross-referencing the patient's allergy history.

## Phase 3: Enhanced Communication & Scheduling
*Goal: Robust real-time interaction.*

1.  **Video Conferencing Stability:**
    *   Harden the current WebRTC/Socket.IO implementation (handle reconnections, multiple participants).
    *   Add a simple text chat sidecar for the video call.
2.  **Schedule Manager:**
    *   Implement a calendar system for doctors to manage virtual appointments.
    *   Notification system for patients (Simple web notifications or simulated SMS/Email).

## Phase 4: Advanced Analytics & Predictive Modeling
*Goal: The "Statistical Insights" and "Generational Data" vision.*

1.  **Predictive Health Dashboard:**
    *   Use historical data to visualize health trends (e.g., rising BP over 5 years).
    *   Implement simple statistical models to predict future risks (e.g., Diabetes risk based on BMI/History).
2.  **Family Tree & Genetic Insights:**
    *   Add "Family Linkage" features to track hereditary conditions across patient profiles.
3.  **Long-term Storage Strategy:**
    *   Evaluate migrating medical history blobs to a NoSQL database (like MongoDB) for flexibility, while keeping relational data (Users/Cases) in PostgreSQL.

## Phase 5: Scaling & Professionalization (The "Go/React" Pivot)
*Goal: Ensure the platform can handle thousands of concurrent users.*

1.  **Backend Migration (Python -> Go):**
    *   Rewrite performance-critical services (Video signaling, Data ingestion) in **Go** for superior concurrency and scalability.
2.  **Frontend Modernization (Jinja2 -> React):**
    *   Build a Single Page Application (SPA) using **React** for a faster, "app-like" UX.
    *   Implement a proper REST or GraphQL API to serve the frontend.
3.  **Deployment & Security:**
    *   Containerize the app (Docker) for consistent deployment.
    *   Implement HIPAA-compliant data encryption at rest.

---

### Decision Log: Why stay in Python for now?
Given this is a 3rd-year project for 2 credits, the priority is **feature completeness** and **demonstrating the intelligence/logic** (LLM integration, statistical warnings). 
- **Python** allows for rapid prototyping of the recommendation engine and analytics.
- **Go/React** migration is slated for Phase 5 as a "Scalability & Hardening" step once the core logic is proven.
