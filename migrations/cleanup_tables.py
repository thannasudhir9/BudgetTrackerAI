import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def cleanup_database():
    """Drop all tables from the database."""
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped successfully!")

if __name__ == '__main__':
    cleanup_database()
