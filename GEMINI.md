# Gemini Project Context: EPICS Telehealth

This project is a comprehensive medical platform designed to connect patients, general practitioners, and specialists. It facilitates case management, medical history tracking, and real-time video consultations.

## Core Vision & Long-Term Goals

- **Global Specialist Access:** Enable patients in remote areas to connect with specialized doctors globally, bridging the gap between local care and specialized expertise.
- **Longitudinal Medical History:** Store and track complete medical history, vitals, and reports across all cases for lifetime access.
- **Predictive & Preventive Analytics:** Use aggregated medical data and statistical models (including potential LLM integration) to predict future health risks, identify allergies, and suggest preventive measures across generations.
- **Intelligent Specialist Matching:** Recommend specialists based on symptoms, vitals, geographical proximity, budget, and insurance coverage.
- **Collaborative Care:** Enable multiple doctors to work on a single case, sharing reports and treatment plans seamlessly.

## Current Technical Stack (Prototype)

- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python 3.12)
- **Database:** [MySQL](https://www.mysql.com/) with [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) (using `pymysql`)
- **Real-time Communication:** [Flask-SocketIO](https://flask-socketio.readthedocs.io/) (using `gevent` for async support)
- **Authentication:** [Flask-Login](https://flask-login.readthedocs.io/)
- **Frontend:** HTML5, CSS3, JavaScript (WebRTC for video calls)
- **Forms:** [Flask-WTF](https://flask-wtf.readthedocs.io/)

## Future Directions & Scalability

- **Architectural Migration:** Potential shift to **Go (Golang)** for backend services and **React** for the frontend to enhance system scalability, performance, and cross-platform compatibility.
- **Advanced Insights:** Integration of LLMs for symptom-based specialist recommendations and advanced predictive analytics.
- **Scheduling & Resource Management:** Implementation of virtual meeting schedulers and resource management for doctors.

## Project Structure

- `app.py`: Main application entry point, containing routes and Socket.IO event handlers.
- `models.py`: Database schema definitions (User, PatientProfile, DoctorProfile, Case).
- `forms.py`: WTForms definitions for login, registration, and profile/case management.
- `templates/`: Jinja2 templates for the web interface.
- `static/js/`: Client-side JavaScript, including `webrtc.js` for video call logic.
- `goal.md`: Original project requirements and long-term vision.

## Building and Running (Current Prototype)

### Prerequisites
- Python 3.12
- Virtual environment (provided in `venv/`)

### Running the Application
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Run the Flask application:
   ```bash
   python app.py
   ```
   *Note: The application uses `gevent` monkey patching for Socket.IO support.*

## Development Conventions

- **Database:** Uses UUIDs for primary keys in `User` and `Case` models.
- **Async Mode:** Uses `gevent` for Flask-SocketIO.
- **WebRTC:** Implements peer-to-peer video calling using STUN servers and Socket.IO for signaling.
