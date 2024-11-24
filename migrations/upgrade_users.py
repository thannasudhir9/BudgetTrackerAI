from datetime import datetime
import sqlite3
import sys
import os

def upgrade_database():
    """
    Upgrade the database to include new user roles and columns.
    This script:
    1. Creates user table if it doesn't exist
    2. Adds role column with NORMAL as default
    3. Adds is_active column defaulting to True
    4. Adds created_at and last_login columns
    5. Makes the first user a SUPER_ADMIN if no admin exists
    """
    try:
        # Get the database path
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'budget_tracker.db')
        
        print(f"Using database at: {db_path}")
        
        # Create instance directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute('BEGIN TRANSACTION')
        
        # Check if user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new user table with all columns
            cursor.execute('''
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT "normal",
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            print("Created user table with all columns")
        else:
            # Get existing columns and their definitions
            cursor.execute("PRAGMA table_info(user)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            print("Existing columns:", columns)
            
            # Create temporary table with all desired columns
            cursor.execute('''
                CREATE TABLE user_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT "normal",
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Map old columns to new columns
            column_mapping = {
                'id': 'id',
                'name': 'username',  # Map 'name' to 'username'
                'email': 'email',
                'password_hash': 'password_hash'
            }
            
            # Build the column lists for copying data
            old_columns = []
            new_columns = []
            for old_col, new_col in column_mapping.items():
                if old_col in columns:
                    old_columns.append(old_col)
                    new_columns.append(new_col)
            
            old_cols_str = ', '.join(old_columns)
            new_cols_str = ', '.join(new_columns)
            
            # Copy existing data
            cursor.execute(f'''
                INSERT INTO user_new ({new_cols_str})
                SELECT {old_cols_str} FROM user
            ''')
            print(f"Copied data from {old_cols_str} to {new_cols_str}")
            
            # Drop old table and rename new one
            cursor.execute('DROP TABLE user')
            cursor.execute('ALTER TABLE user_new RENAME TO user')
            print("Upgraded user table schema")
        
        # Update existing users to have NORMAL role and active status
        cursor.execute('''
            UPDATE user 
            SET role = COALESCE(role, "normal"),
                is_active = COALESCE(is_active, 1),
                created_at = COALESCE(created_at, CURRENT_TIMESTAMP)
            WHERE role IS NULL OR is_active IS NULL OR created_at IS NULL
        ''')
        print(f"Updated {cursor.rowcount} users with default values")
        
        # Check if any admin exists
        cursor.execute('SELECT COUNT(*) FROM user WHERE role IN ("admin", "super_admin")')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Make the first user a super_admin
            cursor.execute('''
                UPDATE user 
                SET role = "super_admin"
                WHERE id = (SELECT MIN(id) FROM user)
            ''')
            if cursor.rowcount > 0:
                print("Upgraded first user to SUPER_ADMIN")
        
        # Create budget_transaction table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_transaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        print("Ensured budget_transaction table exists")
        
        # Commit changes
        conn.commit()
        print("Database upgrade completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade_database()
