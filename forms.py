from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Role', choices=[('STUDENT', 'Student'), ('HOD', 'Head of Department')], default='STUDENT')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please login or choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ItemForm(FlaskForm):
    type = SelectField('Type', choices=[('LOST', 'Lost'), ('FOUND', 'Found')], validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Category', coerce=int) # We will populate this dynamically in routes
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    date_occurred = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    contact_name = StringField('Your Name', validators=[DataRequired(), Length(max=150)])
    contact_number = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=20)])
    is_high_value = BooleanField('High Value Item (Handed to HOD)')
    assigned_department = SelectField('Department / Location Handed To', choices=[
        ('', 'N/A'),
        ('ADMIN BLOCK', 'Admin Block'),
        ('JNANA JYOTHI', 'Jnana Jyothi'),
        ('COMMERCE DEPT', 'Commerce Dept'),
        ('SCIENCE LABS', 'Science Labs'),
        ('CENTRAL LIBRARY', 'Central Library'),
        ('SPORTS PAVILION', 'Sports Pavilion')
    ])
    submit = SubmitField('Post Item')

class HODPasswordChangeForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ReportForm(FlaskForm):
    reason = TextAreaField('Reason for Reporting', validators=[DataRequired()])
    submit = SubmitField('Submit Report')

class ClaimForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Verify & Claim')