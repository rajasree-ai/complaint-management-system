# remove_default_admin.py
from app import app, db
from models import User

def remove_default_admin():
    with app.app_context():
        # Find and remove the default admin
        default_admin = User.query.filter_by(email='admin@college.edu').first()
        if default_admin:
            db.session.delete(default_admin)
            db.session.commit()
            print("Default admin (admin@college.edu) removed successfully!")
        else:
            print("No default admin found.")
        
        # Ensure Vanitha is admin
        vanitha = User.query.filter_by(email='vanitha.sty3375@gmail.com').first()
        if vanitha:
            vanitha.role = 'admin'
            db.session.commit()
            print(f"Vanitha is now admin: {vanitha.email}")
        else:
            print("Vanitha account not found. Please register first.")

if __name__ == '__main__':
    remove_default_admin()