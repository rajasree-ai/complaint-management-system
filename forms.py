from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Department

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # Student-specific fields
    department = SelectField('Department', choices=[], validators=[DataRequired()])
    year = SelectField('Year', choices=[
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year')
    ], validators=[DataRequired()])
    section = SelectField('Section', choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    parent_name = StringField('Parent/Guardian Name', validators=[DataRequired()])
    parent_phone = StringField('Parent/Guardian Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    
    submit = SubmitField('Register')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        from models import Department
        departments = Department.query.order_by(Department.name).all()
        self.department.choices = [(d.name, d.name) for d in departments] if departments else [('', 'No departments available')]
    
    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        from models import User
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
    mentor_id = SelectField('Assign to Mentor (Optional)', choices=[], coerce=int, default=0)
    submit = SubmitField('Submit Complaint')
class CommentForm(FlaskForm):
    content = TextAreaField('Add a comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')


class UpdateComplaintForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected')
    ])
    assigned_to = SelectField('Assign To', choices=[], coerce=int)
    submit = SubmitField('Update')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send OTP')


class ResetPasswordForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset Password')


class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired()])
    hod_id = SelectField('Department Head (HOD)', choices=[], coerce=int)
    submit = SubmitField('Add Department')
    
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        users = User.query.all()
        self.hod_id.choices = [(0, 'Select HOD')] + [(u.id, f"{u.username} ({u.email})") for u in users]