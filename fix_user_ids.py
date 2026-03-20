# fix_user_ids.py
from app import app, db
from models import User, Complaint, Comment, Notification
from sqlalchemy import text

def fix_user_ids():
    with app.app_context():
        # Temporarily disable foreign key checks
        db.session.execute(text('PRAGMA foreign_keys=OFF'))
        
        # Get all users ordered by current ID
        users = User.query.order_by(User.id).all()
        
        # Create a mapping of old IDs to new IDs
        id_mapping = {}
        new_id = 1
        
        for user in users:
            old_id = user.id
            if old_id != new_id:
                id_mapping[old_id] = new_id
                
                # Update user ID
                db.session.execute(
                    text('UPDATE user SET id = :new_id WHERE id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                
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
                
                # Update comments user_id
                db.session.execute(
                    text('UPDATE comment SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                
                # Update notifications user_id
                db.session.execute(
                    text('UPDATE notification SET user_id = :new_id WHERE user_id = :old_id'),
                    {'new_id': new_id, 'old_id': old_id}
                )
                
                print(f"User ID {old_id} -> {new_id}")
            
            new_id += 1
        
        # Re-enable foreign key checks
        db.session.execute(text('PRAGMA foreign_keys=ON'))
        db.session.commit()
        
        print(f"\n✅ Fixed {len(id_mapping)} user IDs. Now IDs are sequential 1,2,3...")

if __name__ == '__main__':
    fix_user_ids()