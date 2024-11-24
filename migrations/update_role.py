from app import app, db, User, UserRole
from sqlalchemy import text

def update_role():
    with app.app_context():
        # First update the role format in the database
        db.session.execute(text("UPDATE user SET role = UPPER(role)"))
        db.session.commit()
        
        # Now update the user's role to NORMAL
        current_user = User.query.first()
        if current_user:
            print(f'Current user: {current_user.username}, Role: {current_user.role}')
            current_user.role = UserRole.NORMAL
            db.session.commit()
            print(f'Updated role: {current_user.role}')
        else:
            print('No users found in the database')

if __name__ == '__main__':
    update_role()
