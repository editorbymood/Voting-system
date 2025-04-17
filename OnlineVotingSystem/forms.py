from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CandidateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    party = StringField('Party', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    description = TextAreaField('Description', validators=[DataRequired()])
    photo_url = StringField('Photo URL', validators=[Length(max=255)])
    submit = SubmitField('Submit')

class VoteForm(FlaskForm):
    candidate_id = HiddenField('Candidate ID', validators=[DataRequired()])
    submit = SubmitField('Vote')
