import random
import string
import re
from datetime import datetime, timedelta, timezone
from models import Complaint, Notification, PasswordResetOTP, Department, User
from database import db
from email_service import send_email


def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt is None:
        return None
    # Assuming local timezone is IST (+5:30), adjust as needed
    local_tz = timezone(timedelta(hours=5, minutes=30))
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)


def generate_complaint_id():
    """Generate sequential complaint ID in format ESEC01, ESEC02, etc."""
    from models import Complaint
    
    latest_complaint = Complaint.query.order_by(Complaint.id.desc()).first()
    
    if latest_complaint and latest_complaint.complaint_id:
        match = re.search(r'ESEC(\d+)', latest_complaint.complaint_id)
        if match:
            last_number = int(match.group(1))
            new_number = last_number + 1
        else:
            new_number = 1
    else:
        new_number = 1
    
    if new_number <= 99:
        return f'ESEC{new_number:02d}'
    else:
        return f'ESEC{new_number:03d}'


def send_email_notification(recipient_email, subject, body, mail=None):
    """Send email notification"""
    html_content = body.replace('\n', '<br>')
    try:
        success = send_email(recipient_email, subject, html_content)
        if success:
            print(f"✅ Email sent to {recipient_email}")
            return True
        print(f"❌ Failed to send email to {recipient_email}")
        return False
    except Exception as e:
        print(f"❌ Error sending email to {recipient_email}: {e}")
        return False


def send_complaint_registration_email(complaint, mail=None):
    """Send email when complaint is registered"""
    subject = f'Complaint Registered: {complaint.complaint_id}'
    body = f'''
Dear {complaint.author.username},

Your complaint has been successfully registered.

Complaint Details:
------------------
Complaint ID: {complaint.complaint_id}
Title: {complaint.title}
Category: {complaint.category}
Priority: {complaint.priority}
Department: {complaint.author.department}
Date: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}

You can track your complaint status at your dashboard.

Thank you,
Complaint Management System
'''
    return send_email_notification(complaint.author.email, subject, body, mail)


def send_comment_notification(complaint, comment, mail=None):
    """Send email when a comment is added to a complaint"""
    subject = f'New Comment on Complaint: {complaint.complaint_id}'
    body = f'''
Dear {complaint.author.username},

A new comment has been added to your complaint.

Complaint: {complaint.title}
Comment by: {comment.user.username}
Comment: {comment.content}
Date: {comment.created_at.strftime('%Y-%m-%d %H:%M')}

View your complaint in your dashboard.

Thank you,
Complaint Management System
'''
    return send_email_notification(complaint.author.email, subject, body, mail)


def send_status_update_email(complaint, old_status, mail=None):
    """Send email when complaint status changes"""
    subject = f'Complaint Status Updated: {complaint.complaint_id}'
    body = f'''
Dear {complaint.author.username},

The status of your complaint has been updated.

Complaint ID: {complaint.complaint_id}
Title: {complaint.title}
Previous Status: {old_status}
New Status: {complaint.status}
Updated Date: {complaint.updated_at.strftime('%Y-%m-%d %H:%M')}

View your complaint in your dashboard.

Thank you,
Complaint Management System
'''
    return send_email_notification(complaint.author.email, subject, body, mail)


def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email, otp, mail=None):
    """Send OTP for password reset"""
    subject = 'Password Reset OTP'
    body = f'''
Dear User,

You requested to reset your password for the Complaint Management System.

Your OTP is: {otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Thank you,
Complaint Management System
'''
    return send_email_notification(email, subject, body, mail)


def create_notification(user_id, complaint_id, message, notification_type='status_update'):
    """Create in-app notification"""
    try:
        notification = Notification(
            user_id=user_id,
            complaint_id=complaint_id if complaint_id else None,
            message=message,
            type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        db.session.rollback()
        return False


def calculate_complaint_stats(complaints):
    """Calculate statistics for complaints"""
    total = len(complaints)
    pending = sum(1 for c in complaints if c.status == 'pending')
    in_progress = sum(1 for c in complaints if c.status == 'in_progress')
    resolved = sum(1 for c in complaints if c.status == 'resolved')
    rejected = sum(1 for c in complaints if c.status == 'rejected')
    
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'rejected': rejected,
        'resolution_rate': round((resolved / total * 100) if total > 0 else 0, 2)
    }


def get_department_users(department):
    """Get all users in a department"""
    return User.query.filter_by(department=department).all()


def get_hod_department(hod_id):
    """Get department where user is HOD"""
    return Department.query.filter_by(hod_id=hod_id).first()


def get_hod_department_by_name(department_name):
    """Get department by name"""
    return Department.query.filter_by(name=department_name).first()


def get_user_department(user_id):
    """Get department of a user"""
    user = User.query.get(user_id)
    return user.department if user else None


def is_hod_of_department(user_id, department_name):
    """Check if user is HOD of a department"""
    department = Department.query.filter_by(name=department_name).first()
    return department and department.hod_id == user_id


def get_department_hod(department_name):
    """Get HOD of a department"""
    department = Department.query.filter_by(name=department_name).first()
    return User.query.get(department.hod_id) if department else None