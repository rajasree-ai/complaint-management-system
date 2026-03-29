# create_student.py
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("=" * 60)
    print("Creating Test Student")
    print("=" * 60)
    
    # Create test student
    student = User.query.filter_by(email='student@college.edu').first()
    if not student:
        student = User(
            username='teststudent',
            email='student@college.edu',
            password=generate_password_hash('student123'),
            role='student',
            department='Computer Science',
            year='1st Year',
            section='A',
            phone='9876543210',
            parent_name='Parent Name',
            parent_phone='9876543211',
            address='Student Address'
        )
        db.session.add(student)
        db.session.commit()
        print("✅ Test student created!")
        print("   Email: student@college.edu")
        print("   Password: student123")
        print("   Department: Computer Science")
    else:
        print("⚠️ Student already exists")
        print(f"   Email: {student.email}")
        print(f"   Department: {student.department}")