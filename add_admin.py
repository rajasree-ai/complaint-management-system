# add_admin.py
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def add_vanitha_admin():
    with app.app_context():
        # Check if vanitha already exists
        vanitha = User.query.filter_by(email='vanitha.sty3375@gmail.com').first()
        
        if vanitha:
            # Update existing user to admin
            vanitha.role = 'admin'
            vanitha.password = generate_password_hash('vanitha@75')
            print(f"Updated {vanitha.email} to admin role")
        else:
            # Create new admin
            vanitha = User(
                username='vanitha',
                email='vanitha.sty3375@gmail.com',
                password=generate_password_hash('vanitha@75'),
                role='admin',
                department='Administration'
            )
            db.session.add(vanitha)
            print("Created new admin: vanitha.sty3375@gmail.com")
        
        db.session.commit()
        print("Password set to: vanitha@75")

if __name__ == '__main__':
    add_vanitha_admin()