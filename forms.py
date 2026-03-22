from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], validators=[DataRequired()])
    submit = SubmitField('Register')

class PatientProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    medical_history = TextAreaField('Medical History (Persistent)', validators=[DataRequired()])
    
    # Phase 1 fields
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    insurance_info = StringField('Insurance Information', validators=[Optional(), Length(max=200)])
    budget_limit = IntegerField('Budget Limit (Numeric)', validators=[Optional()])
    
    submit = SubmitField('Save Profile')

class DoctorProfileForm(FlaskForm):
    specialization = StringField('Specialization', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class CaseForm(FlaskForm):
    symptoms = TextAreaField('Current Symptoms', validators=[DataRequired()])
    
    # Phase 1: Vitals
    bp = StringField('Blood Pressure (e.g., 120/80)', validators=[Optional()])
    heart_rate = IntegerField('Heart Rate (bpm)', validators=[Optional()])
    spo2 = IntegerField('SpO2 (%)', validators=[Optional()])
    temperature = FloatField('Temperature (°C)', validators=[Optional()])
    
    submit = SubmitField('Submit Case')

class VillageDoctorCaseForm(CaseForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    is_village_doctor_initiated = BooleanField('Opening on behalf of patient', default=True)

class ReportUploadForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    report_file = FileField('Medical Report (PDF or Image)', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'PDFs and Images only!')
    ])
    submit = SubmitField('Upload Report')

class AssignSpecialistForm(FlaskForm):
    specialist_id = SelectField('Select Specialist', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Specialist')
