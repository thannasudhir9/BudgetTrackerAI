import sqlite3
from datetime import datetime

def add_timestamp_columns():
    # Connect to the database
    conn = sqlite3.connect('budget_tracker.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add created_at if it doesn't exist
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN created_at TIMESTAMP")
            # Set default value for existing rows
            cursor.execute("UPDATE user SET created_at = ? WHERE created_at IS NULL", (datetime.utcnow(),))
        
        # Add updated_at if it doesn't exist
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN updated_at TIMESTAMP")
            # Set default value for existing rows
            cursor.execute("UPDATE user SET updated_at = ? WHERE updated_at IS NULL", (datetime.utcnow(),))
        
        conn.commit()
        print("Successfully added timestamp columns to user table")
        
    except Exception as e:
        print(f"Error adding timestamp columns: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_timestamp_columns()
