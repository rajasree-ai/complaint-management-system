from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail
from datetime import datetime, timedelta
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from database import db, login_manager
from models import User, Complaint, Comment, Notification
from forms import RegistrationForm, LoginForm, ComplaintForm, CommentForm, UpdateComplaintForm
from utils import generate_complaint_id, send_email_notification, create_notification, calculate_complaint_stats

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and admin user
with app.app_context():
    db.create_all()
    
    # Create Vanitha as admin
    vanitha_admin = User.query.filter_by(email='vanitha.sty3375@gmail.com').first()
    if not vanitha_admin:
        vanitha_admin = User(
            username='vanitha',
            email='vanitha.sty3375@gmail.com',
            password=generate_password_hash('vanitha@75'),
            role='admin',
            department='Administration'
        )
        db.session.add(vanitha_admin)
        db.session.commit()
        print("Admin account created!")

# ========== ROUTES ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            department=form.department.data,
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        complaints = Complaint.query.filter_by(user_id=current_user.id).all()
        stats = calculate_complaint_stats(complaints)
        notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return render_template('dashboard.html', complaints=complaints, stats=stats, notifications=notifications)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    complaints = Complaint.query.all()
    users = User.query.all()
    stats = calculate_complaint_stats(complaints)
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    return render_template('admin_dashboard.html', complaints=complaints, users=users, stats=stats, recent_complaints=recent_complaints)

# ⚠️ THIS IS THE ROUTE YOU NEED - MAKE SURE IT EXISTS ⚠️
@app.route('/complaint/new', methods=['GET', 'POST'])
@login_required
def new_complaint():
    form = ComplaintForm()
    if form.validate_on_submit():
        complaint = Complaint(
            complaint_id=generate_complaint_id(),
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            priority=form.priority.data,
            user_id=current_user.id
        )
        db.session.add(complaint)
        db.session.commit()
        flash('Your complaint has been submitted!', 'success')
        return redirect(url_for('view_complaints'))
    return render_template('create_complaint.html', form=form)

@app.route('/complaints')
@login_required
def view_complaints():
    # Get search parameters
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    
    query = Complaint.query
    
    # Apply filters
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user.id)
    
    if search_query:
        query = query.filter(
            Complaint.complaint_id.ilike(f'%{search_query}%') |
            Complaint.title.ilike(f'%{search_query}%')
        )
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    
    # Get filter options
    categories = Complaint.query.with_entities(Complaint.category).distinct().all()
    statuses = ['pending', 'in_progress', 'resolved', 'rejected']
    
    return render_template('view_complaints.html', 
                         complaints=complaints,
                         categories=[c[0] for c in categories],
                         statuses=statuses,
                         search_query=search_query,
                         category_filter=category_filter,
                         status_filter=status_filter)

@app.route('/complaint/<int:complaint_id>', methods=['GET', 'POST'])
@login_required
def complaint_details(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check if user has permission to view this complaint
    if current_user.role != 'admin' and complaint.user_id != current_user.id:
        abort(403)
    
    comment_form = CommentForm()
    update_form = UpdateComplaintForm()
    
    # Populate assigned_to choices for admin
    if current_user.role == 'admin':
        staff_users = User.query.filter_by(role='staff').all()
        update_form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.username) for u in staff_users]
    
    # Handle comment submission
    if comment_form.validate_on_submit() and 'submit_comment' in request.form:
        comment = Comment(
            content=comment_form.content.data,
            user_id=current_user.id,
            complaint_id=complaint.id
        )
        db.session.add(comment)
        db.session.commit()
        
        # Create notification for complaint owner
        if complaint.user_id != current_user.id:
            create_notification(
                complaint.user_id,
                complaint.id,
                f'New comment on your complaint #{complaint.complaint_id}',
                'comment'
            )
        
        flash('Comment added!', 'success')
        return redirect(url_for('complaint_details', complaint_id=complaint.id))
    
    # ========== HANDLE COMPLAINT UPDATE (ADMIN ONLY) ==========
    if update_form.validate_on_submit() and 'update_complaint' in request.form and current_user.role == 'admin':
        old_status = complaint.status
        
        # Update the complaint
        complaint.status = update_form.status.data
        complaint.assigned_to = update_form.assigned_to.data if update_form.assigned_to.data != 0 else None
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"Complaint updated: Status changed from {old_status} to {complaint.status}")  # Debug
        
        # Send notification to user if status changed
        if old_status != complaint.status:
            create_notification(
                complaint.user_id,
                complaint.id,
                f'Your complaint status has been updated from {old_status} to {complaint.status}',
                'status_update'
            )
            
            # Send email notification
            try:
                subject = f'Complaint Status Updated: {complaint.complaint_id}'
                body = f'''Your complaint status has been updated.
                
Complaint ID: {complaint.complaint_id}
Title: {complaint.title}
New Status: {complaint.status}
Previous Status: {old_status}
                
Login to view more details.
'''
                send_email_notification(complaint.author.email, subject, body, mail)
            except Exception as e:
                print(f"Email error: {e}")
        
        flash(f'Complaint status updated from {old_status} to {complaint.status}!', 'success')
        return redirect(url_for('complaint_details', complaint_id=complaint.id))
    
    return render_template('complaint_details.html', 
                         complaint=complaint, 
                         comment_form=comment_form,
                         update_form=update_form)
@app.route('/complaint/<int:complaint_id>/resolve')
@login_required
def resolve_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Only admin or assigned staff can resolve
    if current_user.role != 'admin' and current_user.id != complaint.assigned_to:
        abort(403)
    
    old_status = complaint.status
    complaint.status = 'resolved'
    complaint.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify user
    create_notification(
        complaint.user_id,
        complaint.id,
        f'Your complaint has been marked as resolved!',
        'status_update'
    )
    
    flash(f'Complaint marked as resolved! Status changed from {old_status} to resolved.', 'success')
    return redirect(url_for('complaint_details', complaint_id=complaint.id))
@app.route('/complaint/<int:complaint_id>/delete', methods=['POST'])
@login_required
def delete_complaint(complaint_id):
    """Delete a resolved or rejected complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check if user has permission to delete
    if current_user.role == 'admin':
        # Admin can delete any resolved/rejected complaint
        pass
    elif current_user.role == 'staff' and complaint.assigned_to == current_user.id:
        # Staff can delete resolved/rejected complaints assigned to them
        pass
    elif complaint.user_id == current_user.id:
        # User can delete their own resolved/rejected complaints
        pass
    else:
        flash('You do not have permission to delete this complaint.', 'danger')
        return redirect(url_for('complaint_details', complaint_id=complaint.id))
    
    # Allow deletion of resolved OR rejected complaints
    if complaint.status not in ['resolved', 'rejected']:
        flash('Only resolved or rejected complaints can be deleted!', 'warning')
        return redirect(url_for('complaint_details', complaint_id=complaint.id))
    
    try:
        # Store complaint info for flash message
        complaint_id_display = complaint.complaint_id
        complaint_title = complaint.title
        complaint_status = complaint.status
        
        # Delete related comments first
        Comment.query.filter_by(complaint_id=complaint.id).delete()
        
        # Delete related notifications
        Notification.query.filter_by(complaint_id=complaint.id).delete()
        
        # Delete the complaint
        db.session.delete(complaint)
        db.session.commit()
        
        flash(f'Complaint "{complaint_title}" (ID: {complaint_id_display}) - Status: {complaint_status} has been deleted successfully!', 'success')
        
        # Redirect based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('view_complaints'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting complaint: {str(e)}', 'danger')
        return redirect(url_for('complaint_details', complaint_id=complaint.id))
@app.route('/notifications')
@login_required
def view_notifications():
    """View all notifications for the current user"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=notifications)
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/admin/users')
@login_required
def manage_users():
    """Admin page to manage all users"""
    if current_user.role != 'admin':
        abort(403)
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)


# 👇 ADD THIS RIGHT HERE 👇
@app.route('/admin/user/<int:user_id>/change-role/<string:role>')
@login_required
def change_user_role(user_id, role):
    """Change a user's role (admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        flash('You cannot change your own role!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Validate role
    if role not in ['student', 'staff']:
        flash('Invalid role specified!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Update user role
    old_role = user.role
    user.role = role
    db.session.commit()
    
    flash(f'User role changed from {old_role} to {role} for {user.username}', 'success')
    
    # Create notification for the user about role change (optional)
    try:
        create_notification(
            user.id,
            None,
            f'Your account role has been changed from {old_role} to {role}',
            'role_change'
        )
    except:
        pass
    
    return redirect(url_for('manage_users'))
@app.route('/fix-ids')
@login_required
def fix_ids():
    """Temporary route to fix user IDs - REMOVE AFTER USE"""
    if current_user.role != 'admin':
        return "Only admin can access this", 403
    
    try:
        from sqlalchemy import text
        
        # Get all users ordered by current ID
        users = User.query.order_by(User.id).all()
        fixed_count = 0
        
        print(f"Found {len(users)} users")
        
        for new_id, user in enumerate(users, start=1):
            old_id = user.id
            if old_id != new_id:
                print(f"Updating {user.username}: ID {old_id} → {new_id}")
                
                # Update user ID
                db.session.execute(
                    text('UPDATE "user" SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                
                # Update references in other tables
                db.session.execute(
                    text('UPDATE complaint SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                db.session.execute(
                    text('UPDATE comment SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                db.session.execute(
                    text('UPDATE notification SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                fixed_count += 1
        
        db.session.commit()
        
        # Get updated users to display
        updated_users = User.query.order_by(User.id).all()
        result = "<h2>✅ IDs Fixed!</h2><ul>"
        for user in updated_users:
            result += f"<li>ID {user.id}: {user.username} ({user.email})</li>"
        result += f"</ul><p>Fixed {fixed_count} users.</p>"
        result += "<p><a href='/manage_users'>Go to Manage Users</a></p>"
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {str(e)}"
@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user account (admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    try:
        # Store username for flash message
        username = user.username
        
        # Delete all complaints by this user
        Complaint.query.filter_by(user_id=user.id).delete()
        
        # Delete all comments by this user
        Comment.query.filter_by(user_id=user.id).delete()
        
        # Delete all notifications for this user
        Notification.query.filter_by(user_id=user.id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User "{username}" has been deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('manage_users'))


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_own_account():
    """Allow users to delete their own account"""
    user = current_user
    
    try:
        username = user.username
        
        # Delete all complaints by this user
        Complaint.query.filter_by(user_id=user.id).delete()
        
        # Delete all comments by this user
        Comment.query.filter_by(user_id=user.id).delete()
        
        # Delete all notifications for this user
        Notification.query.filter_by(user_id=user.id).delete()
        
        # Logout the user first
        logout_user()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Your account "{username}" has been deleted successfully!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {str(e)}', 'danger')
        return redirect(url_for('profile'))
if __name__ == '__main__':
    app.run(debug=True)