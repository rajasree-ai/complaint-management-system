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
    
    # Check which departments already exist
    existing_names = {dept.name for dept in Department.query.all()}
    added_count = 0
    for dept_name in departments:
        if dept_name not in existing_names:
            db.session.add(Department(name=dept_name))
            print(f"Added department: {dept_name}")
            added_count += 1
    
    if added_count > 0:
        db.session.commit()
        print(f"\n✅ Added {added_count} new departments successfully!")
    else:
        print(f"No new departments were added. {len(existing_names)} departments already exist.")