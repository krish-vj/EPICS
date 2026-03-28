# 1. USE GEVENT MONKEY PATCH (Standard for modern Flask-SocketIO)
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, emit
from models import db, User, PatientProfile, DoctorProfile, Case, Report
from forms import LoginForm, RegisterForm, PatientProfileForm, DoctorProfileForm, CaseForm, VillageDoctorCaseForm, ReportUploadForm, AssignSpecialistForm, PrescriptionForm, ScheduleMeetingForm
import os
import math
from datetime import datetime
from google import genai
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()  # This loads the variables from .env into os.environ
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost/telehealth')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 2. INITIALIZE SOCKETIO WITH GEVENT
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# Track users in video rooms and their socket IDs
video_rooms = {}
user_sockets = {}  # Maps user_id to socket_id

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

# Configure Gemini
import google.genai
print(f"--- SDK DEBUG: genai library location: {google.genai.__file__} ---")
print("--- SDK STATUS: INITIALIZING GOOGLE-GENAI SDK (FORCED V1) ---")
# Force API version to v1 to avoid v1beta redirects
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'}
)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth in km."""
    if None in [lat1, lon1, lat2, lon2]: return float('inf')
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_specialist_recommendation(symptoms, vitals):
    """Use Gemini to recommend a specialist type based on symptoms and vitals."""
    prompt = f"""
    Based on the following patient symptoms and vitals, recommend the MOST appropriate medical specialist category (e.g., Cardiologist, Dermatologist, Gynecologist, General Physician, etc.).
    
    Symptoms: {symptoms}
    Vitals: {vitals}
    
    Provide ONLY the category name as the output.
    """
    
    # Try multiple stable models available in 2026
    models_to_try = [ 'gemini-2.5-flash']
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "404" in str(e):
                print(f"Gemini: Model {model_name} not found, trying next...")
                continue
            if "503" in str(e) or "high demand" in str(e).lower():
                print(f"Gemini API: High demand (503) on {model_name}. Falling back.")
                return "General Physician"
            print(f"Gemini Error on {model_name}: {e}")
            break
            
    return "General Physician"

@app.route('/api/search_patients')
@login_required
def search_patients():
    q = request.args.get('q', '')
    if len(q) < 2: return jsonify([])
    
    # Search for patients by username
    users = User.query.filter(User.role == 'patient', User.username.ilike(f'%{q}%')).limit(10).all()
    results = []
    for u in users:
        if u.patient_profile:
            results.append({
                'username': u.username,
                'name': u.patient_profile.name,
                'age': u.patient_profile.age
            })
    return jsonify(results)

@app.route('/api/search_specialists')
@login_required
def search_specialists():
    q = request.args.get('q', '')
    if len(q) < 2: return jsonify([])
    
    # Search for approved doctors by username or specialization
    users = User.query.join(DoctorProfile).filter(
        User.role == 'doctor',
        DoctorProfile.is_approved == True,
        (User.username.ilike(f'%{q}%') | DoctorProfile.specialization.ilike(f'%{q}%'))
    ).limit(10).all()
    
    results = []
    for u in users:
        results.append({
            'username': u.username,
            'specialization': u.doctor_profile.specialization
        })
    return jsonify(results)

@app.route('/api/suggest_category', methods=['POST'])
@login_required
def suggest_category():
    data = request.get_json()
    symptoms = data.get('symptoms', '')
    if not symptoms:
        return jsonify({'category': None})
    
    # Use existing Gemini logic
    category = get_specialist_recommendation(symptoms, "Not provided")
    return jsonify({'category': category})

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        if user.role == 'patient':
            prof = PatientProfile(
                user_id=user.id,
                name=form.full_name.data,
                age=form.age.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data
            )
            db.session.add(prof)
        elif user.role == 'doctor':
            prof = DoctorProfile(
                user_id=user.id,
                specialization=form.specialization.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data
            )
            db.session.add(prof)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Admin Section ---
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    unapproved_docs = DoctorProfile.query.filter_by(is_approved=False).all()
    return render_template('admin_dashboard.html', doctors=unapproved_docs)

@app.route('/admin/approve/<int:doc_id>')
@login_required
def approve_doctor(doc_id):
    if current_user.role != 'admin': return redirect(url_for('index'))
    doc = db.session.get(DoctorProfile, doc_id)
    if doc:
        doc.is_approved = True
        db.session.commit()
        flash(f'Doctor {doc.user.username} approved.')
    return redirect(url_for('admin_dashboard'))

# --- Patient Section ---
@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient': return redirect(url_for('index'))
    profile = current_user.patient_profile
    my_cases = Case.query.filter_by(patient_profile_id=profile.id).order_by(Case.created_at.desc()).all()
    return render_template('patient_dashboard.html', profile=profile, cases=my_cases)

@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'patient': return redirect(url_for('index'))
    profile = current_user.patient_profile
    form = PatientProfileForm(obj=profile)
    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        flash('Profile updated.')
        return redirect(url_for('patient_dashboard'))
    return render_template('edit_profile.html', form=form)

@app.route('/patient/create_case', methods=['GET', 'POST'])
@login_required
def create_case():
    if current_user.role != 'patient': return redirect(url_for('index'))
    form = CaseForm()
    if form.validate_on_submit():
        new_case = Case(
            patient_profile_id=current_user.patient_profile.id,
            symptoms=form.symptoms.data,
            required_specialist=form.required_specialist.data or None,
            bp=form.bp.data,
            heart_rate=form.heart_rate.data,
            spo2=form.spo2.data,
            temperature=form.temperature.data
        )
        db.session.add(new_case)
        db.session.commit()
        flash('Case submitted successfully.')
        return redirect(url_for('patient_dashboard'))
    return render_template('create_case.html', form=form)

# --- Doctor Section ---
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor': return redirect(url_for('index'))
    doc_profile = current_user.doctor_profile
    if not doc_profile.is_approved:
        return render_template('doctor_pending.html')
    
    # Smart Triage Logic:
    # 1. If doc is "General Physician", they see cases with NULL specialist req or 'General Physician'.
    # 2. If doc is a specialist (e.g., 'Cardiologist'), they see cases tagged specifically for them.
    if doc_profile.specialization == 'General Physician':
        open_cases = Case.query.filter(
            Case.status == 'open',
            (Case.required_specialist == None) | (Case.required_specialist == 'General Physician')
        ).order_by(Case.created_at.asc()).limit(20).all()
    else:
        # Specialists see their specific cases OR general cases? 
        # Usually specialists want to see what they are assigned to.
        # Let's show them cases matching their specialization.
        open_cases = Case.query.filter(
            Case.status == 'open',
            Case.required_specialist == doc_profile.specialization
        ).order_by(Case.created_at.asc()).limit(20).all()

    my_general_cases = Case.query.filter_by(doctor_profile_id=doc_profile.id).all()
    my_specialist_cases = Case.query.filter_by(specialist_profile_id=doc_profile.id).all()
    
    return render_template('doctor_dashboard.html', 
                           open_cases=open_cases, 
                           my_general_cases=my_general_cases,
                           my_specialist_cases=my_specialist_cases)

@app.route('/doctor/profile', methods=['GET', 'POST'])
@login_required
def doctor_profile():
    if current_user.role != 'doctor': return redirect(url_for('index'))
    profile = current_user.doctor_profile
    form = DoctorProfileForm(obj=profile)
    if form.validate_on_submit():
        form.populate_obj(profile)
        db.session.commit()
        flash('Profile updated.')
        return redirect(url_for('doctor_dashboard'))
    return render_template('edit_profile.html', form=form, role='doctor')

@app.route('/doctor/create_case', methods=['GET', 'POST'])
@login_required
def doctor_create_case():
    """Village Doctor flow: Open case on behalf of patient using username"""
    if current_user.role != 'doctor': return redirect(url_for('index'))
    form = VillageDoctorCaseForm()
    
    if form.validate_on_submit():
        patient_user = User.query.filter_by(username=form.patient_username.data, role='patient').first()
        if not patient_user or not patient_user.patient_profile:
            flash('Patient username not found.')
            return render_template('create_case.html', form=form, is_doctor=True)
            
        new_case = Case(
            patient_profile_id=patient_user.patient_profile.id,
            doctor_profile_id=current_user.doctor_profile.id,
            symptoms=form.symptoms.data,
            required_specialist=form.required_specialist.data or None,
            bp=form.bp.data,
            heart_rate=form.heart_rate.data,
            spo2=form.spo2.data,
            temperature=form.temperature.data,
            is_village_doctor_initiated=True,
            status='active'
        )
        db.session.add(new_case)
        db.session.commit()
        flash(f'Case created on behalf of {patient_user.username}.')
        return redirect(url_for('doctor_dashboard'))
    return render_template('create_case.html', form=form, is_doctor=True)

@app.route('/doctor/accept/<case_id>')
@login_required
def accept_case(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    if case and case.status == 'open':
        case.doctor_profile_id = current_user.doctor_profile.id
        case.status = 'active'
        db.session.commit()
        flash('Case accepted.')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/case/<case_id>', methods=['GET', 'POST'])
@login_required
def view_case(case_id):
    case = db.session.get(Case, case_id)
    if not case:
        flash("Case not found.")
        return redirect(url_for('index'))

    # Permission Check:
    # 1. Doctors assigned to the case
    # 2. The patient who owns the case
    is_assigned_doctor = False
    if current_user.role == 'doctor':
        doc_id = current_user.doctor_profile.id
        if case.doctor_profile_id == doc_id or case.specialist_profile_id == doc_id:
            is_assigned_doctor = True
    
    is_owner_patient = False
    if current_user.role == 'patient':
        if case.patient_profile_id == current_user.patient_profile.id:
            is_owner_patient = True

    if not (is_assigned_doctor or is_owner_patient):
        flash("You do not have permission to view this case.")
        return redirect(url_for('index'))
    
    report_form = ReportUploadForm()
    assign_form = AssignSpecialistForm()
    prescription_form = PrescriptionForm()
    meeting_form = ScheduleMeetingForm()
    
    # Parse prescriptions for frontend
    parsed_prescriptions = []
    if case.prescriptions:
        raw_list = case.prescriptions.split('\with(')
        for item in raw_list:
            if ')' in item:
                parts = item.split(')', 1)
                if len(parts) == 2:
                    parsed_prescriptions.append({'date': parts[0], 'text': parts[1]})
    
    return render_template('case_detail.html', 
                           case=case, 
                           report_form=report_form, 
                           assign_form=assign_form,
                           prescription_form=prescription_form,
                           meeting_form=meeting_form,
                           parsed_prescriptions=parsed_prescriptions[::-1]) # Show newest first

@app.route('/doctor/case/<case_id>/add_prescription', methods=['POST'])
@login_required
def add_prescription(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    form = PrescriptionForm()
    if form.validate_on_submit():
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f"\with({now_str}){form.medicine_details.data}"
        if case.prescriptions:
            case.prescriptions += new_entry
        else:
            case.prescriptions = new_entry
        db.session.commit()
        flash('Prescription added.')
    return redirect(url_for('view_case', case_id=case_id))

@app.route('/doctor/case/<case_id>/schedule_meeting', methods=['POST'])
@login_required
def schedule_meeting(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    form = ScheduleMeetingForm()
    if form.validate_on_submit():
        try:
            m_time = datetime.strptime(form.meeting_time.data, '%Y-%m-%d %H:%M')
            case.next_meeting_time = m_time
            case.next_meeting_notes = form.notes.data
            db.session.commit()
            flash('Meeting scheduled.')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD HH:MM')
    return redirect(url_for('view_case', case_id=case_id))

@app.route('/doctor/case/<case_id>/close', methods=['POST'])
@login_required
def close_case(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    doc_id = current_user.doctor_profile.id
    
    if case and (case.doctor_profile_id == doc_id or case.specialist_profile_id == doc_id):
        case.status = 'closed'
        db.session.commit()
        flash('Case closed successfully.')
    else:
        flash('Unauthorized to close this case.')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/case/<case_id>/reject', methods=['POST'])
@login_required
def reject_case(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    doc_id = current_user.doctor_profile.id
    
    if case:
        if case.specialist_profile_id == doc_id:
            case.specialist_profile_id = None
            db.session.commit()
            flash('You have declined the specialist role for this case.')
        elif case.doctor_profile_id == doc_id:
            case.doctor_profile_id = None
            case.status = 'open'
            db.session.commit()
            flash('You have rejected this case. It is now open for other doctors.')
        else:
            flash('You are not assigned to this case.')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/case/<case_id>/upload_report', methods=['POST'])
@login_required
def upload_report(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    form = ReportUploadForm()
    if form.validate_on_submit():
        file = form.report_file.data
        if file:
            filename = secure_filename(f"{case_id}_{datetime.utcnow().timestamp()}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            report = Report(
                case_id=case_id,
                file_path=filename,
                file_type=file.filename.split('.')[-1].upper(),
                description=form.description.data
            )
            db.session.add(report)
            db.session.commit()
            flash('Report uploaded successfully.')
    return redirect(url_for('view_case', case_id=case_id))

@app.route('/doctor/case/<case_id>/assign_specialist', methods=['POST'])
@login_required
def assign_specialist(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    form = AssignSpecialistForm()
    
    if form.validate_on_submit():
        specialist_user = User.query.filter_by(username=form.specialist_username.data, role='doctor').first()
        if not specialist_user or not specialist_user.doctor_profile:
            flash('Specialist username not found.')
            return redirect(url_for('view_case', case_id=case_id))
            
        case.specialist_profile_id = specialist_user.doctor_profile.id
        db.session.commit()
        flash(f'Specialist {specialist_user.username} assigned to the case.')
    return redirect(url_for('view_case', case_id=case_id))

@app.route('/video_call/<room_id>')
@login_required
def video_call(room_id):
    return render_template('video_call.html', room_id=room_id, username=current_user.username)

@app.route('/doctor/recommend_doctor/<case_id>')
@login_required
def recommend_doctor(case_id):
    print(f"DEBUG: recommend_doctor called for case_id: {case_id}")
    if current_user.role != 'doctor': return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        case = db.session.get(Case, case_id)
        if not case: return jsonify({'error': 'Case not found'}), 404
        
        # 1. Get Specialist Category from Gemini
        vitals = f"BP: {case.bp}, HR: {case.heart_rate}, SpO2: {case.spo2}, Temp: {case.temperature}"
        recommended_category = get_specialist_recommendation(case.symptoms, vitals)
        
        # 2. Search for doctors based on category
        potential_docs = DoctorProfile.query.filter(
            DoctorProfile.is_approved == True,
            DoctorProfile.specialization.ilike(f"%{recommended_category}%")
        ).all()
        
        if not potential_docs:
            potential_docs = DoctorProfile.query.filter(DoctorProfile.is_approved == True).all()
            
        results = []
        patient = case.patient_profile
        if not patient:
            return jsonify({'error': 'Patient profile not found for this case'}), 400
            
        for doc in potential_docs:
            dist = haversine(patient.latitude, patient.longitude, doc.latitude, doc.longitude)
            availability_score = doc.active_cases_count
            ranking_score = dist + (availability_score * 10)
            
            results.append({
                'doc_id': doc.id,
                'name': doc.user.username if doc.user else "Unknown Doctor",
                'specialization': doc.specialization,
                'distance_km': round(dist, 2),
                'active_cases': availability_score,
                'ranking_score': ranking_score
            })
        
        results.sort(key=lambda x: x['ranking_score'])
        
        return jsonify({
            'recommended_category': recommended_category,
            'doctors': results[:5]
        })
    except Exception as e:
        print(f"Error in recommend_doctor: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- Socket Events ---

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    if current_user.is_authenticated:
        # Map user_id to socket_id
        user_sockets[current_user.id] = request.sid
        print(f"User {current_user.username} (ID: {current_user.id}) mapped to socket {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Remove from user_sockets mapping
    for user_id, sid in list(user_sockets.items()):
        if sid == request.sid:
            del user_sockets[user_id]
            print(f"Removed user {user_id} from socket mapping")
    
    # Clean up any rooms this user was in
    for room_id, users in list(video_rooms.items()):
        if request.sid in users:
            users.remove(request.sid)
            emit('user_left', {'sid': request.sid}, room=room_id)
            if len(users) == 0:
                del video_rooms[room_id]

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    print(f"User {request.sid} joined room {room}")
    
    # If it's a user notification room, just join it
    if room.startswith('user_'):
        return
    
    # Track users in video room
    if room not in video_rooms:
        video_rooms[room] = []
    
    if request.sid not in video_rooms[room]:
        video_rooms[room].append(request.sid)
    
    print(f"Room {room} now has {len(video_rooms[room])} users")
    
    # If there are 2 users, signal ready to start call
    if len(video_rooms[room]) == 2:
        caller_sid = video_rooms[room][0]
        emit('ready', {'message': 'Second user joined, start call'}, room=caller_sid)
        print(f"Signaling ready to caller {caller_sid}")

@socketio.on('initiate_call')
def handle_initiate_call(data):
    """Doctor initiates a call to patient"""
    patient_user_id = data['patient_user_id']
    room_id = data['room_id']
    
    print(f"Call initiation: Doctor {current_user.username} calling patient {patient_user_id}")
    print(f"Room ID: {room_id}")
    print(f"Current user_sockets mapping: {user_sockets}")
    
    # Find patient's socket ID
    patient_socket_id = user_sockets.get(patient_user_id)
    
    if patient_socket_id:
        print(f"Found patient socket: {patient_socket_id}")
        # Send notification to patient's specific socket
        emit('incoming_call', {
            'room_id': room_id,
            'caller': current_user.username
        }, room=patient_socket_id)
        print(f"Sent incoming_call notification to patient")
    else:
        print(f"Patient {patient_user_id} not connected (not in user_sockets)")
        # You might want to emit an error back to the doctor
        emit('call_failed', {
            'message': 'Patient is not currently online'
        }, room=request.sid)

@socketio.on('offer')
def handle_offer(data):
    room = data['room']
    offer = data['offer']
    print(f"Received offer for room {room}")
    emit('offer', {'offer': offer}, room=room, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    room = data['room']
    answer = data['answer']
    print(f"Received answer for room {room}")
    emit('answer', {'answer': answer}, room=room, include_self=False)

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    room = data['room']
    candidate = data['candidate']
    emit('ice_candidate', {'candidate': candidate}, room=room, include_self=False)

@socketio.on('end_call')
def handle_end_call(data):
    room = data['room']
    print(f"Call ended in room {room}")
    emit('call_ended', {'room': room}, room=room)
    
    # Clean up room
    if room in video_rooms:
        for user_sid in video_rooms[room]:
            leave_room(room, sid=user_sid)
        del video_rooms[room]

# --- Init DB & Admin ---
def init_db():
    with app.app_context():
        # Drop and Recreate for fresh start if needed (User should manually drop tables as discussed)
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            
            # 1. Seed 30 Doctors
            specs = ['General Physician', 'Cardiologist', 'Dermatologist', 'Gynecologist', 'Neurologist', 'Pediatrician']
            for i in range(1, 31):
                username = f'doc{i}'
                if not User.query.filter_by(username=username).first():
                    u = User(username=username, role='doctor')
                    u.set_password('password')
                    db.session.add(u)
                    db.session.flush()
                    
                    # Cycle through specializations
                    spec = specs[i % len(specs)]
                    # Random coordinates around a central point (e.g., Bhopal, India: 23.25, 77.41)
                    lat = 23.25 + (i * 0.01)
                    lng = 77.41 + (i * 0.01)
                    
                    d = DoctorProfile(
                        user_id=u.id, 
                        specialization=spec, 
                        is_approved=True, # Auto-approve for testing
                        latitude=lat,
                        longitude=lng
                    )
                    db.session.add(d)

            # 2. Seed 30 Patients
            for i in range(1, 31):
                username = f'patient{i}'
                if not User.query.filter_by(username=username).first():
                    u = User(username=username, role='patient')
                    u.set_password('password')
                    db.session.add(u)
                    db.session.flush()
                    
                    lat = 23.20 + (i * 0.005)
                    lng = 77.35 + (i * 0.005)
                    
                    p = PatientProfile(
                        user_id=u.id,
                        name=f'Patient Name {i}',
                        age=20 + i,
                        medical_history="No significant history." if i%2==0 else "Allergic to Penicillin.",
                        latitude=lat,
                        longitude=lng
                    )
                    db.session.add(p)
            
            db.session.commit()
            print("Database Seeded: Admin(admin), 30 Doctors(doc1-30), 30 Patients(patient1-30). Passwords: 'password' or 'admin'")

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
