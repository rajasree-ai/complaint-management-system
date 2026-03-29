from app import app, db
from models import Department

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # List of default departments
    departments = [
        'Computer Science and Engineering',
        'Information Technology', 
        'Electronics and Communication Engineering',
        'Electrical and Electronics Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Artificial Intelligence and Data Science',
        'Artificial Intelligence and Machine Learning',
        'Computer Science and Design',
        'Biomedical Engineering',
        'Robotics and Automation',
        'Chemical Engineering',
        'Agricultural Engineering',
        'Biotechnology',
        'Cyber Security',
        'MBA',
        'MCA'
    ]
    
    # Check if departments already exist
    existing_depts = Department.query.all()
    
    if not existing_depts:
        for dept_name in departments:
            dept = Department(name=dept_name)
            db.session.add(dept)
            print(f"Added department: {dept_name}")
        
        db.session.commit()
        print(f"\n✅ Added {len(departments)} departments successfully!")
    else:
        print(f"Departments already exist: {len(existing_depts)} found")
        for dept in existing_depts:
            print(f"  - {dept.name}")