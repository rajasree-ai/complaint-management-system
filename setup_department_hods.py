# setup_department_hods.py
from app import app, db
from models import User, Department
from werkzeug.security import generate_password_hash

with app.app_context():
    # Department list with their HOD credentials
    departments = [
        {'name': 'Computer Science', 'hod_username': 'hod_cs', 'hod_email': 'hod.cs@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Information Technology', 'hod_username': 'hod_it', 'hod_email': 'hod.it@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Electronics and Communication', 'hod_username': 'hod_ec', 'hod_email': 'hod.ec@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Electrical and Electronics', 'hod_username': 'hod_ee', 'hod_email': 'hod.ee@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Mechanical Engineering', 'hod_username': 'hod_mech', 'hod_email': 'hod.mech@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Civil Engineering', 'hod_username': 'hod_civil', 'hod_email': 'hod.civil@college.edu', 'hod_password': 'hod@123'},
        {'name': 'Artificial Intelligence and Data Science', 'hod_username': 'hod_ads', 'hod_email': 'hod.ads@college.edu', 'hod_password': 'hod@123'},
    ]
    
    print("=" * 60)
    print("Setting up Department HODs")
    print("=" * 60)
    
    for dept_data in departments:
        # Create or get department
        department = Department.query.filter_by(name=dept_data['name']).first()
        if not department:
            department = Department(name=dept_data['name'])
            db.session.add(department)
            db.session.commit()
            print(f"✅ Created department: {dept_data['name']}")
        
        # Create HOD user
        hod = User.query.filter_by(email=dept_data['hod_email']).first()
        if not hod:
            hod = User(
                username=dept_data['hod_username'],
                email=dept_data['hod_email'],
                password=generate_password_hash(dept_data['hod_password']),
                role='hod',
                department=dept_data['name']
            )
            db.session.add(hod)
            db.session.commit()
            print(f"✅ Created HOD: {dept_data['hod_username']} ({dept_data['hod_email']}) for {dept_data['name']}")
        else:
            # Update existing user to HOD role
            hod.role = 'hod'
            hod.department = dept_data['name']
            db.session.commit()
            print(f"✅ Updated HOD: {hod.username} for {dept_data['name']}")
        
        # Link department to HOD
        department.hod_id = hod.id
        db.session.commit()
    
    print("\n" + "=" * 60)
    print("✅ All Department HODs Created Successfully!")
    print("=" * 60)
    print("\nHOD Login Credentials:")
    print("-" * 40)
    for dept in departments:
        print(f"{dept['name']}: {dept['hod_email']} / {dept['hod_password']}")
    print("\nMain Admin: vanitha.sty3375@gmail.com / vanitha@75")