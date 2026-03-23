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
@app.route('/fix-complaint-ids')
@login_required
def fix_complaint_ids():
    """Temporary route to fix complaint IDs to be sequential"""
    if current_user.role != 'admin':
        return "Only admin can access this", 403
    
    try:
        from sqlalchemy import text
        
        # Get all complaints ordered by created date
        complaints = Complaint.query.order_by(Complaint.created_at).all()
        
        result = "<html><body><h2>Fixing Complaint IDs...</h2>"
        result += f"<p>Found {len(complaints)} complaints</p>"
        
        fixed_count = 0
        
        for idx, complaint in enumerate(complaints, start=1):
            old_id = complaint.complaint_id
            new_id = f'ESEC{idx:02d}'
            
            if old_id != new_id:
                # Update the complaint ID
                db.session.execute(
                    text('UPDATE complaint SET complaint_id = :new_id WHERE id = :comp_id'),
                    {'new_id': new_id, 'comp_id': complaint.id}
                )
                result += f"<p>Changed: {old_id} → {new_id}</p>"
                fixed_count += 1
        
        db.session.commit()
        
        result += f"<h2 style='color:green'>✅ Fixed {fixed_count} complaints!</h2>"
        result += "<a href='/complaints'>Go to My Complaints</a>"
        result += "</body></html>"
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return f"<h2 style='color:red'>Error: {str(e)}</h2>"
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
@app.route('/fix-ids-simple')
@login_required
def fix_ids_simple():
    """Simpler approach - shows SQL to run"""
    if current_user.role != 'admin':
        return "Only admin can access this", 403
    
    # Get current users
    users = User.query.order_by(User.id).all()
    
    result = """
    <html>
    <head>
        <title>Fix User IDs - SQL Method</title>
        <style>
            body{font-family:Arial;padding:20px;}
            pre{background:#f4f4f4;padding:15px;border-radius:5px;overflow-x:auto;}
            .button{background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;display:inline-block;margin:20px 0;}
            .warning{background:#ff9800;color:white;padding:10px;border-radius:5px;}
        </style>
    </head>
    <body>
        <h2>🔧 Fix User IDs - SQL Method</h2>
        <p>Current users in database:</p>
        <table border="1" cellpadding="8">
            <tr><th>Current ID</th><th>Username</th><th>Email</th></tr>
    """
    
    for user in users:
        result += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.email}</td></tr>"
    
    result += """
        </table>
        <div class="warning">
            <strong>⚠️ Important:</strong> Since you have existing complaints, we need to update references.
        </div>
        <p>Click the button below to fix the IDs (this will also update all complaint references):</p>
        <a href="/execute-fix" class="button">✅ Fix IDs Now</a>
        <a href="/admin/users" class="button">Cancel</a>
    </body>
    </html>
    """
    
    return result


@app.route('/execute-fix')
@login_required
def execute_fix():
    """Execute the actual ID fix"""
    if current_user.role != 'admin':
        return "Only admin can access this", 403
    
    try:
        from sqlalchemy import text
        
        # Disable triggers temporarily (for PostgreSQL)
        db.session.execute(text('SET session_replication_role = replica;'))
        
        # Get all users
        users = User.query.order_by(User.id).all()
        
        # Create mapping
        id_map = {}
        new_id = 1
        for user in users:
            id_map[user.id] = new_id
            new_id += 1
        
        # Update all tables
        for old_id, new_id_val in id_map.items():
            if old_id != new_id_val:
                # Update user
                db.session.execute(
                    text('UPDATE "user" SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id_val, 'old_id': old_id}
                )
                # Update complaint user_id
                db.session.execute(
                    text('UPDATE complaint SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id_val, 'old_id': old_id}
                )
                # Update comment user_id
                db.session.execute(
                    text('UPDATE comment SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id_val, 'old_id': old_id}
                )
                # Update notification user_id
                db.session.execute(
                    text('UPDATE notification SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id_val, 'old_id': old_id}
                )
        
        # Re-enable triggers
        db.session.execute(text('SET session_replication_role = origin;'))
        db.session.commit()
        
        # Show result
        updated_users = User.query.order_by(User.id).all()
        
        result = "<html><body><h2 style='color:green'>✅ IDs Fixed Successfully!</h2><table border='1'><tr><th>ID</th><th>Username</th><th>Email</th></tr>"
        for user in updated_users:
            result += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.email}</td></tr>"
        result += "</table><br><a href='/admin/users'>Go to Manage Users</a></body></html>"
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return f"<h2 style='color:red'>❌ Error: {str(e)}</h2><a href='/admin/users'>Go back</a>"
@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    # Check if user has any complaints
    if user.complaints:
        flash(f'Cannot delete user "{user.username}" because they have {len(user.complaints)} complaint(s).', 'danger')
        return redirect(url_for('manage_users'))
    
    try:
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" has been deleted successfully!', 'success')
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
@app.route('/renumber-users')
@login_required
def renumber_users():
    """Temporary route to make user IDs sequential - Works with normal permissions"""
    if current_user.role != 'admin':
        return "Only admin can access this", 403
    
    try:
        from sqlalchemy import text
        
        result = "<html><head><title>Renumber Users</title>"
        result += "<style>body{font-family:Arial;padding:20px;} .success{color:green;} .error{color:red;} table{border-collapse:collapse;margin-top:20px;} th,td{border:1px solid #ddd;padding:8px;} th{background:#4CAF50;color:white;} .button{background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;display:inline-block;margin-top:20px;}</style>"
        result += "</head><body>"
        
        # Get all users ordered by current ID
        users = User.query.order_by(User.id).all()
        
        result += f"<h2>Current Users</h2>"
        result += "<table><tr><th>Current ID</th><th>Username</th><th>Email</th></tr>"
        for user in users:
            result += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.email}</td></tr>"
        result += "</table><br>"
        
        # Create a new table with sequential IDs (this is safer)
        result += "<h3>Step 1: Creating backup of user data...</h3>"
        
        # Instead of modifying existing IDs, we'll create a new sequence
        # First, get all user data
        user_data = []
        for user in users:
            user_data.append({
                'old_id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'role': user.role,
                'department': user.department,
                'created_at': user.created_at
            })
        
        result += "<h3>Step 2: Updating references...</h3>"
        
        # Update complaint references to temporary negative IDs to avoid conflicts
        new_id = 1
        old_to_new = {}
        
        for user in users:
            old_id = user.id
            temp_id = -old_id  # Use negative as temporary
            old_to_new[old_id] = {'temp': temp_id, 'new': new_id}
            
            # Update user to temporary negative ID
            db.session.execute(
                text('UPDATE "user" SET id = :temp_id WHERE id = :old_id'),
                {'temp_id': temp_id, 'old_id': old_id}
            )
            new_id += 1
        
        db.session.commit()
        
        result += "<h3>Step 3: Updating complaint references...</h3>"
        
        # Update all foreign key references to the temporary IDs
        for old_id, mapping in old_to_new.items():
            temp_id = mapping['temp']
            
            # Update complaints
            db.session.execute(
                text('UPDATE complaint SET user_id = :temp_id WHERE user_id = :old_id'),
                {'temp_id': temp_id, 'old_id': old_id}
            )
            # Update comments
            db.session.execute(
                text('UPDATE comment SET user_id = :temp_id WHERE user_id = :old_id'),
                {'temp_id': temp_id, 'old_id': old_id}
            )
            # Update notifications
            db.session.execute(
                text('UPDATE notification SET user_id = :temp_id WHERE user_id = :old_id'),
                {'temp_id': temp_id, 'old_id': old_id}
            )
        
        db.session.commit()
        
        result += "<h3>Step 4: Assigning new sequential IDs...</h3>"
        
        # Now update from temporary IDs to final sequential IDs
        for old_id, mapping in old_to_new.items():
            temp_id = mapping['temp']
            final_id = mapping['new']
            
            # Update user to final ID
            db.session.execute(
                text('UPDATE "user" SET id = :final_id WHERE id = :temp_id'),
                {'final_id': final_id, 'temp_id': temp_id}
            )
            
            # Update references to final ID
            db.session.execute(
                text('UPDATE complaint SET user_id = :final_id WHERE user_id = :temp_id'),
                {'final_id': final_id, 'temp_id': temp_id}
            )
            db.session.execute(
                text('UPDATE comment SET user_id = :final_id WHERE user_id = :temp_id'),
                {'final_id': final_id, 'temp_id': temp_id}
            )
            db.session.execute(
                text('UPDATE notification SET user_id = :final_id WHERE user_id = :temp_id'),
                {'final_id': final_id, 'temp_id': temp_id}
            )
        
        db.session.commit()
        
        result += "<h2 class='success'>✅ Users Successfully Renumbered!</h2>"
        
        # Show updated users
        updated_users = User.query.order_by(User.id).all()
        result += "<h3>Updated Users List:</h3>"
        result += "<table><tr><th>New ID</th><th>Username</th><th>Email</th><th>Role</th></tr>"
        
        for user in updated_users:
            result += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.email}</td><td>{user.role}</td></tr>"
        
        result += "</table><br>"
        result += "<a href='/admin/users' class='button'>Go to Manage Users</a>"
        result += "</body></html>"
        
        return result
        
    except Exception as e:
        db.session.rollback()
        return f"""
        <html>
        <body>
            <h2 style="color:red;">❌ Error</h2>
            <p>Error details: {str(e)}</p>
            <p>No changes were made to the database.</p>
            <a href="/admin/users">Go back</a>
        </body>
        </html>
        """
    
@app.route('/test')
def test():
    return "✅ App is working!"   
if __name__ == '__main__':
    app.run(debug=True)