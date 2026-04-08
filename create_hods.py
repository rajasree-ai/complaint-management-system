# create_hods.py
from app import app, db
from models import User, Department
from werkzeug.security import generate_password_hash

with app.app_context():
    print("=" * 60)
    print("Creating Department HODs")
    print("=" * 60)
    
    # List of departments with HOD credentials
    hods = [
        {'username': 'hod_cs', 'email': 'hod.cs@college.edu', 'password': 'hod@123', 'department': 'Computer Science'},
        {'username': 'hod_it', 'email': 'hod.it@college.edu', 'password': 'hod@123', 'department': 'Information Technology'},
        {'username': 'hod_ec', 'email': 'hod.ec@college.edu', 'password': 'hod@123', 'department': 'Electronics and Communication'},
        {'username': 'hod_ee', 'email': 'hod.ee@college.edu', 'password': 'hod@123', 'department': 'Electrical and Electronics'},
        {'username': 'hod_mech', 'email': 'hod.mech@college.edu', 'password': 'hod@123', 'department': 'Mechanical Engineering'},
        {'username': 'hod_civil', 'email': 'hod.civil@college.edu', 'password': 'hod@123', 'department': 'Civil Engineering'},
        {'username': 'hod_ads', 'email': 'hod.ads@college.edu', 'password': 'hod@123', 'department': 'Artificial Intelligence and Data Science'},
    ]
    
    created_count = 0
    existing_count = 0
    
    for hod_data in hods:
        # Check if HOD already exists
        existing = User.query.filter_by(email=hod_data['email']).first()
        if not existing:
            hod = User(
                username=hod_data['username'],
                email=hod_data['email'],
                password=generate_password_hash(hod_data['password']),
                role='hod',
                department=hod_data['department']
            )
            db.session.add(hod)
            print(f"✅ Created HOD: {hod_data['department']} - {hod_data['email']}")
            created_count += 1
        else:
            print(f"⚠️ HOD already exists: {hod_data['email']}")
            existing_count += 1
    
    db.session.commit()
    
    print("\n" + "=" * 60)
    print(f"✅ Created {created_count} new HODs")
    print(f"⚠️ {existing_count} HODs already existed")
    print("=" * 60)