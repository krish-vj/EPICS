from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], validators=[DataRequired()])
    submit = SubmitField('Register')

class PatientHistoryForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    medical_history = TextAreaField('Medical History (Persistent)', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class CaseForm(FlaskForm):
    symptoms = TextAreaField('Current Symptoms', validators=[DataRequired()])
    submit = SubmitField('Submit Case')
