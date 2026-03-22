# fix_user_ids.py
from app import app, db
from models import User

def fix_user_ids():
    with app.app_context():
        # Get users ordered by current ID
        users = User.query.order_by(User.id).all()
        
        # Get existing user IDs
        old_ids = [user.id for user in users]
        
        # Update each user with new sequential ID
        for new_id, user in enumerate(users, start=1):
            old_id = user.id
            if old_id != new_id:
                # Direct SQL update for SQLite
                db.session.execute(
                    'UPDATE "user" SET id = ? WHERE id = ?',
                    (new_id, old_id)
                )
                print(f"User ID {old_id} → {new_id}")
        
        db.session.commit()
        print("✅ Done! User IDs are now sequential.")

if __name__ == '__main__':
    fix_user_ids()