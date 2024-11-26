import os
import sqlite3
from flask import Flask

def cleanup_database():
    app = Flask(__name__, instance_relative_config=True)
    db_path = os.path.join(app.instance_path, 'budget_tracker.db')
    
    print(f"Cleaning up database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Commit changes
        conn.commit()
        print("All tables have been dropped successfully!")
        
    except Exception as e:
        print(f"Error cleaning up database: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    cleanup_database()
