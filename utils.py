import random
import string
from datetime import datetime
from flask_mail import Message

# Don't import models at the top level to avoid circular imports
# We'll import inside functions where needed

from models import Complaint
from sqlalchemy import func

def generate_complaint_id():
    """Generate sequential complaint ID in format ESEC01, ESEC02, etc."""
    # Get the highest existing complaint number
    latest_complaint = Complaint.query.order_by(Complaint.id.desc()).first()
    
    if latest_complaint and latest_complaint.complaint_id:
        # Extract the number from the latest complaint ID (ESEC01 -> 1)
        try:
            # Handle both formats: ESEC01 and ESEC001
            import re
            match = re.search(r'ESEC(\d+)', latest_complaint.complaint_id)
            if match:
                last_number = int(match.group(1))
                new_number = last_number + 1
            else:
                new_number = 1
        except (ValueError, IndexError):
            new_number = 1
    else:
        # First complaint, start from 1
        new_number = 1
    
    # Format with leading zeros (01, 02, 03...)
    if new_number <= 99:
        return f'ESEC{new_number:02d}'
    else:
        return f'ESEC{new_number:03d}'


def send_email_notification(recipient_email, subject, body, mail):
    """Send email notification"""
    try:
        msg = Message(subject, recipients=[recipient_email])
        msg.body = body
        mail.send(msg)
        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
def create_notification(user_id, complaint_id, message, notification_type='status_update'):
    """Create in-app notification"""
    from models import Notification
    from database import db
    
    try:
        notification = Notification(
            user_id=user_id,
            complaint_id=complaint_id if complaint_id else None,  # Handle None
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


def get_department_users(department):
    """Get all users in a department"""
    # Import inside function to avoid circular imports
    from models import User
    
    try:
        return User.query.filter_by(department=department, role='staff').all()
    except Exception as e:
        print(f"Error getting department users: {e}")
        return []


def calculate_complaint_stats(complaints):
    """Calculate statistics for complaints"""
    total = len(complaints)
    pending = sum(1 for c in complaints if c.status == 'pending')
    in_progress = sum(1 for c in complaints if c.status == 'in_progress')
    resolved = sum(1 for c in complaints if c.status == 'resolved')
    rejected = sum(1 for c in complaints if c.status == 'rejected')
    
    # Calculate resolution rate
    if total > 0:
        resolution_rate = round((resolved / total) * 100, 2)
    else:
        resolution_rate = 0
    
    print(f"Stats calculated - Total: {total}, Pending: {pending}, In Progress: {in_progress}, Resolved: {resolved}, Rejected: {rejected}")  # Debug print
    
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'rejected': rejected,
        'resolution_rate': resolution_rate
    }

def migrate_to_esec_format():
    """Migrate existing complaints to ESEC format (run once)"""
    # Import inside function to avoid circular imports
    from models import Complaint
    from database import db
    
    try:
        complaints = Complaint.query.all()
        count = 0
        
        for index, complaint in enumerate(complaints, start=1):
            # Check if already in ESEC format
            if not complaint.complaint_id or not complaint.complaint_id.startswith('ESEC'):
                # Assign new sequential ID
                if index <= 99:
                    complaint.complaint_id = f'ESEC{index:02d}'
                else:
                    complaint.complaint_id = f'ESEC{index:03d}'
                count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Migrated {count} complaints to ESEC format")
        else:
            print("No complaints needed migration")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        db.session.rollback()


def get_next_complaint_number():
    """Helper function to get the next complaint number"""
    from models import Complaint
    
    try:
        # Get all ESEC formatted complaints
        complaints = Complaint.query.filter(
            Complaint.complaint_id.like('ESEC%')
        ).all()
        
        max_number = 0
        for complaint in complaints:
            try:
                num = int(complaint.complaint_id[4:])
                if num > max_number:
                    max_number = num
            except (ValueError, IndexError):
                continue
        
        return max_number + 1
        
    except Exception as e:
        print(f"Error getting next complaint number: {e}")
        return 1