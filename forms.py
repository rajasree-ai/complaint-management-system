from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    department = StringField('Department')
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ComplaintForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('academic', 'Academic'),
        ('administrative', 'Administrative'),
        ('facility', 'Facility'),
        ('harassment', 'Harassment'),
        ('technical', 'Technical'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    submit = SubmitField('Submit Complaint')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Add Comment')

class UpdateComplaintForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected')
    ])
    assigned_to = SelectField('Assign To', choices=[], coerce=int)
    submit = SubmitField('Update')