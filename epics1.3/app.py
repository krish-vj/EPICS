# 1. USE GEVENT MONKEY PATCH (Standard for modern Flask-SocketIO)
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room, emit
from models import db, User, PatientProfile, DoctorProfile, Case
from forms import LoginForm, RegisterForm, PatientHistoryForm, CaseForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///telehealth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
            prof = PatientProfile(user_id=user.id)
            db.session.add(prof)
        elif user.role == 'doctor':
            prof = DoctorProfile(user_id=user.id)
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
    form = PatientHistoryForm(obj=profile)
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
            symptoms=form.symptoms.data
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
    open_cases = Case.query.filter_by(status='open').all()
    my_cases = Case.query.filter_by(doctor_profile_id=doc_profile.id).all()
    return render_template('doctor_dashboard.html', open_cases=open_cases, my_cases=my_cases)

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

@app.route('/doctor/case/<case_id>')
@login_required
def view_case(case_id):
    if current_user.role != 'doctor': return redirect(url_for('index'))
    case = db.session.get(Case, case_id)
    if case.doctor_profile_id != current_user.doctor_profile.id:
        flash("You are not assigned to this case.")
        return redirect(url_for('doctor_dashboard'))
    return render_template('case_detail.html', case=case)

@app.route('/video_call/<room_id>')
@login_required
def video_call(room_id):
    return render_template('video_call.html', room_id=room_id, username=current_user.username)

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
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin created (admin/admin)")

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)