# add_sample_data.py
from app import app, db
from models import User, Complaint
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

with app.app_context():
    print("=" * 50)
    print("Adding Sample Data to Complaint System")
    print("=" * 50)
    
    # Check if we have students
    students = User.query.filter_by(role='student').all()
    
    if not students:
        print("❌ No students found! Creating a sample student...")
        
        # Create a sample student
        student = User(
            username='rajasree',
            email='rajasree@student.edu',
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
        students = [student]
        print("✅ Sample student created!")
        print("   Email: rajasree@student.edu")
        print("   Password: student123")
    else:
        print(f"✅ Found {len(students)} existing students")
        for s in students:
            print(f"   - {s.username} ({s.email})")
    
    # Check existing complaints
    existing_count = Complaint.query.count()
    print(f"\nExisting complaints: {existing_count}")
    
    if existing_count == 0:
        print("\nAdding sample complaints...")
        
        complaint_titles = [
            "Network connectivity issues in Computer Lab",
            "Library needs more reference books for AI/DS",
            "Canteen food quality needs improvement",
            "AC not working in Classroom 301",
            "Hostel water supply irregular in evening",
            "Transportation bus timing issues",
            "Exam schedule conflict with placement activities",
            "Lab equipment in Electronics lab not functioning",
            "Faculty response time for doubts too slow",
            "Parking space for students insufficient",
            "WiFi connectivity issues in hostel",
            "Classroom projector not working properly",
            "Library timings need extension during exams",
            "Sports equipment needs replacement",
            "Medical facility in campus needs improvement"
        ]
        
        categories = ['academic', 'facility', 'administrative', 'technical']
        statuses = ['pending', 'in_progress', 'resolved', 'rejected']
        priorities = ['low', 'medium', 'high']
        
        count = 0
        for i in range(8):
            student = random.choice(students)
            complaint = Complaint(
                complaint_id=f'ESEC{count+1:02d}',
                title=random.choice(complaint_titles),
                description=f"This is a sample complaint. Please look into this matter at the earliest. The issue has been ongoing for several days.",
                category=random.choice(categories),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                user_id=student.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
            )
            db.session.add(complaint)
            count += 1
        
        db.session.commit()
        print(f"✅ Added {count} sample complaints!")
    else:
        print(f"✅ Already have {existing_count} complaints in the system.")
    
    print("\n" + "=" * 50)
    print("Current Complaints in System:")
    print("=" * 50)
    complaints = Complaint.query.all()
    if complaints:
        for c in complaints:
            print(f"ID: {c.complaint_id} | Title: {c.title[:40]} | Status: {c.status} | Student: {c.author.username}")
    else:
        print("No complaints found.")