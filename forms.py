from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

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
    submit = SubmitField('Post Item')

class ReportForm(FlaskForm):
    reason = TextAreaField('Reason for Reporting', validators=[DataRequired()])
    submit = SubmitField('Submit Report')

class ClaimForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired(), Length(min=8, max=8)])
    submit = SubmitField('Verify & Claim')