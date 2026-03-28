# EPICS Telehealth: Global Specialist Access & Predictive Care

**EPICS Telehealth** is a comprehensive medical platform designed to bridge the gap between patients in remote areas and specialized medical expertise globally. Developed as a 3rd-year CSE project, this platform facilitates seamless case management, longitudinal medical history tracking, and real-time video consultations.

## 🌟 The Vision

In many remote areas, patients only have access to general practitioners. Our platform enables "Village Doctors" to capture vitals and symptoms, which are then used by an AI-driven matching engine to connect patients with the right specialists—regardless of geographical barriers. 

Beyond immediate care, the platform tracks medical history across a patient's lifetime (and across generations) to provide predictive insights and preventive health measures using statistical modeling.

## 🚀 Key Features

- **Collaborative Case Management:** Allows general practitioners and multiple specialists to collaborate on a single patient case with shared access to reports and history.
- **AI Specialist Matching (LLM-Powered):** Integrates LLMs (Gemini API) to recommend specialists based on symptoms, vitals, and medical history.
- **Intelligent Discovery:** Doctors are filtered based on specialization, geographical proximity, and the patient's budget or insurance coverage.
- **Real-Time Consultations:** Built-in WebRTC video calling for virtual face-to-face meetings between doctors and patients.
- **Predictive Health Analytics:** Tracks trends in vitals over years to predict future health risks and prevent potential complications.
- **Safety & Allergy Alerts:** Automatically cross-references new prescriptions against a patient's historical allergy data to prevent adverse reactions.

## 🛠️ Tech Stack (Current Prototype)

- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python 3.12)
- **Database:** MySQL with [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) (using `pymysql`)
- **Real-time Communication:** [Flask-SocketIO](https://flask-socketio.readthedocs.io/) (with `gevent`)
- **Video Calling:** WebRTC with STUN servers
- **Authentication:** [Flask-Login](https://flask-login.readthedocs.io/)
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript, Jinja2 Templates

## 🗺️ Implementation Roadmap

### Phase 1: Clinical Foundation
- [x] Basic Profile Management
- [x] Structured Vitals Tracking (BP, SpO2, Temp)
- [x] Secure Medical Report Uploads (PDF/Images)

### Phase 2: Intelligence Layer
- [x] Gemini API Integration for specialist recommendations
- [x] Proximity & Budget-based Search Algorithm
- [ ] Automated Allergy & Conflict Warning System

### Phase 3: Enhanced UX
- [x] Hardened WebRTC for low-bandwidth environments
- [ ] Integrated Doctor Scheduling & Calendar Management
- [ ] Real-time Text Chat during video calls

### Phase 4: Advanced Analytics
- [ ] Predictive Health Dashboard for long-term trends
- [ ] Genetic & Family Tree Data Linkage for hereditary risk analysis

### Phase 5: Scaling (Future Migration)
- [ ] Backend Migration to **Go** for high-concurrency scaling
- [ ] Frontend Modernization with **React** for a faster SPA experience

## 🏁 Getting Started

### Prerequisites
- Python 3.12+
- Virtual Environment

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/epics-telehealth.git
   cd epics-telehealth
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`.

---
*Developed as part of the EPICS (Engineering Projects in Community Service) program.*
