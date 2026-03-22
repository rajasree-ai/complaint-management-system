# manual_fix.py
from app import app, db
from models import User

with app.app_context():
    # Get the second user (ID 5)
    second_user = User.query.filter_by(username='Rajasree M').first()
    
    if second_user and second_user.id != 2:
        # Update ID to 2
        db.session.execute(
            'UPDATE "user" SET id = 2 WHERE id = ?',
            (second_user.id,)
        )
        
        # Update any complaints (if any)
        db.session.execute(
            'UPDATE complaint SET user_id = 2 WHERE user_id = ?',
            (second_user.id,)
        )
        
        db.session.commit()
        print(f"Updated {second_user.username} from ID {second_user.id} to 2")
    
    print("✅ Done!")