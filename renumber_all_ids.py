# renumber_all_ids.py
from app import app, db
from models import User, Complaint, Department, Comment, Notification
from sqlalchemy import text

def renumber_all_ids():
    with app.app_context():
        print("=" * 60)
        print("RENUMBERING ALL IDs TO SEQUENTIAL ORDER")
        print("=" * 60)
        
        # Disable foreign key checks
        db.session.execute(text('PRAGMA foreign_keys=OFF'))
        
        # ========== 1. RENUMBER USERS ==========
        print("\n📋 1. Renumbering Users...")
        users = User.query.order_by(User.id).all()
        print(f"   Found {len(users)} users")
        
        user_id_map = {}
        new_id = 1
        for user in users:
            old_id = user.id
            if old_id != new_id:
                user_id_map[old_id] = new_id
                print(f"   User {user.username}: ID {old_id} → {new_id}")
                
                # Update user ID
                db.session.execute(
                    text('UPDATE "user" SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
            new_id += 1
        
        # Update references to users
        for old_id, new_id in user_id_map.items():
            # Update complaints user_id
            db.session.execute(
                text('UPDATE complaint SET user_id = :new_id WHERE user_id = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
            # Update complaints assigned_to
            db.session.execute(
                text('UPDATE complaint SET assigned_to = :new_id WHERE assigned_to = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
            # Update comments
            db.session.execute(
                text('UPDATE comment SET user_id = :new_id WHERE user_id = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
            # Update notifications
            db.session.execute(
                text('UPDATE notification SET user_id = :new_id WHERE user_id = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
        
        print(f"   ✅ Renumbered {len(user_id_map)} users")
        
        # ========== 2. RENUMBER COMPLAINTS ==========
        print("\n📋 2. Renumbering Complaints...")
        complaints = Complaint.query.order_by(Complaint.created_at).all()
        print(f"   Found {len(complaints)} complaints")
        
        complaint_id_map = {}
        new_id = 1
        for complaint in complaints:
            old_id = complaint.id
            if old_id != new_id:
                complaint_id_map[old_id] = new_id
                print(f"   Complaint {complaint.complaint_id}: ID {old_id} → {new_id}")
                
                # Update complaint ID
                db.session.execute(
                    text('UPDATE complaint SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
            new_id += 1
        
        # Update references to complaints
        for old_id, new_id in complaint_id_map.items():
            # Update comments complaint_id
            db.session.execute(
                text('UPDATE comment SET complaint_id = :new_id WHERE complaint_id = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
            # Update notifications complaint_id
            db.session.execute(
                text('UPDATE notification SET complaint_id = :new_id WHERE complaint_id = :old_id'),
                {'new_id': new_id, 'old_id': old_id}
            )
        
        print(f"   ✅ Renumbered {len(complaint_id_map)} complaints")
        
        # ========== 3. RENUMBER DEPARTMENTS ==========
        print("\n📋 3. Renumbering Departments...")
        departments = Department.query.order_by(Department.id).all()
        print(f"   Found {len(departments)} departments")
        
        dept_id_map = {}
        new_id = 1
        for dept in departments:
            old_id = dept.id
            if old_id != new_id:
                dept_id_map[old_id] = new_id
                print(f"   Department {dept.name}: ID {old_id} → {new_id}")
                
                # Update department ID
                db.session.execute(
                    text('UPDATE department SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
            new_id += 1
        
        # Update references to departments (hod_id in user table)
        for old_id, new_id in dept_id_map.items():
            # Note: department.hod_id references user, not department
            # No direct foreign key from other tables to department
            pass
        
        print(f"   ✅ Renumbered {len(dept_id_map)} departments")
        
        # ========== 4. RENUMBER COMMENTS (if needed) ==========
        print("\n📋 4. Renumbering Comments...")
        comments = Comment.query.order_by(Comment.id).all()
        print(f"   Found {len(comments)} comments")
        
        comment_id_map = {}
        new_id = 1
        for comment in comments:
            old_id = comment.id
            if old_id != new_id:
                comment_id_map[old_id] = new_id
                print(f"   Comment ID {old_id} → {new_id}")
                
                # Update comment ID
                db.session.execute(
                    text('UPDATE comment SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
            new_id += 1
        
        print(f"   ✅ Renumbered {len(comment_id_map)} comments")
        
        # ========== 5. RENUMBER NOTIFICATIONS (if needed) ==========
        print("\n📋 5. Renumbering Notifications...")
        notifications = Notification.query.order_by(Notification.id).all()
        print(f"   Found {len(notifications)} notifications")
        
        notif_id_map = {}
        new_id = 1
        for notif in notifications:
            old_id = notif.id
            if old_id != new_id:
                notif_id_map[old_id] = new_id
                print(f"   Notification ID {old_id} → {new_id}")
                
                # Update notification ID
                db.session.execute(
                    text('UPDATE notification SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
            new_id += 1
        
        print(f"   ✅ Renumbered {len(notif_id_map)} notifications")
        
        # Re-enable foreign key checks
        db.session.execute(text('PRAGMA foreign_keys=ON'))
        db.session.commit()
        
        # ========== SUMMARY ==========
        print("\n" + "=" * 60)
        print("✅ RENUMBERING COMPLETE!")
        print("=" * 60)
        print(f"   Users renumbered: {len(user_id_map)}")
        print(f"   Complaints renumbered: {len(complaint_id_map)}")
        print(f"   Departments renumbered: {len(dept_id_map)}")
        print(f"   Comments renumbered: {len(comment_id_map)}")
        print(f"   Notifications renumbered: {len(notif_id_map)}")
        print("=" * 60)
        
        # Display results
        print("\n📊 Final Sequential IDs:")
        print("-" * 40)
        
        users = User.query.order_by(User.id).all()
        print(f"\n👥 Users ({len(users)}):")
        for u in users:
            print(f"   ID {u.id}: {u.username} ({u.role})")
        
        complaints = Complaint.query.order_by(Complaint.id).all()
        print(f"\n📝 Complaints ({len(complaints)}):")
        for c in complaints:
            print(f"   ID {c.id}: {c.complaint_id} - {c.title[:30]}...")
        
        departments = Department.query.order_by(Department.id).all()
        print(f"\n🏢 Departments ({len(departments)}):")
        for d in departments:
            print(f"   ID {d.id}: {d.name}")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    renumber_all_ids()