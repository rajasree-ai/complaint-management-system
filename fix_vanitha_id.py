# fix_vanitha_id.py
from app import app, db
from models import User
from sqlalchemy import text

def fix_vanitha_id():
    with app.app_context():
        # Find vanitha
        vanitha = User.query.filter_by(email='vanitha.sty3375@gmail.com').first()
        
        if vanitha:
            if vanitha.id != 1:
                print(f"Vanitha current ID: {vanitha.id}")
                
                # Temporarily disable foreign key checks
                db.session.execute(text('PRAGMA foreign_keys=OFF'))
                
                # Update ID to 1
                db.session.execute(
                    text('UPDATE user SET id = 1 WHERE id = :old_id'),
                    {'old_id': vanitha.id}
                )
                
                # Re-enable foreign key checks
                db.session.execute(text('PRAGMA foreign_keys=ON'))
                
                db.session.commit()
                print("✅ Vanitha ID updated to 1 successfully!")
            else:
                print("✅ Vanitha already has ID 1")
        else:
            print("❌ Vanitha not found in database")

if __name__ == '__main__':
    fix_vanitha_id()