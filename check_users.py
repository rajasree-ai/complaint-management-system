# check_users.py
from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    
    print("\n" + "=" * 80)
    print("📋 ALL USERS IN DATABASE")
    print("=" * 80)
    print(f"{'ID':<4} {'Username':<15} {'Email':<35} {'Role':<10} {'Department'}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<4} {user.username:<15} {user.email:<35} {user.role:<10} {user.department}")
    
    print("=" * 80)
    
    # Count by role
    students = User.query.filter_by(role='student').count()
    staff = User.query.filter_by(role='staff').count()
    hods = User.query.filter_by(role='hod').count()
    admins = User.query.filter_by(role='admin').count()
    
    print(f"\n📊 Summary:")
    print(f"   Students: {students}")
    print(f"   Staff: {staff}")
    print(f"   HODs: {hods}")
    print(f"   Admins: {admins}")
    print("=" * 80)