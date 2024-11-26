import os
import sqlite3
from datetime import datetime

def init_db():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('budget_tracker.db')
    cursor = conn.cursor()

    try:
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS budget_transaction")
        cursor.execute("DROP TABLE IF EXISTS category")
        cursor.execute("DROP TABLE IF EXISTS user")

        # Create user table
        cursor.execute("""
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(128),
            role VARCHAR(20) NOT NULL DEFAULT 'normal',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_login TIMESTAMP
        )
        """)

        # Create category table
        cursor.execute("""
        CREATE TABLE category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            icon VARCHAR(50) DEFAULT 'bi-tag',
            color VARCHAR(50) DEFAULT 'primary',
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        """)

        # Create transaction table
        cursor.execute("""
        CREATE TABLE budget_transaction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description VARCHAR(200) NOT NULL,
            amount FLOAT NOT NULL,
            type VARCHAR(20) NOT NULL,
            date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES category (id),
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
        """)

        # Create default users
        default_users = [
            ('superadmin', 'superadmin@example.com', 'pbkdf2:sha256:600000$X7YaB0pwQxZN1bZI$c89775b7cefb139c8db9a7391f14e43b9e92f920a6e2d2a3cbf0d8405b389b33', 'super_admin'),
            ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$UQqAFq2zxD7XTSJJ$e9c6f7276c4c9c0e6c3db84d1d77b6f8c0fc4c0b9298a8d4155c9c4e7f8a7b0a', 'admin'),
            ('testuser', 'testuser@example.com', 'pbkdf2:sha256:600000$YPR9HZZ0Hs4YQJJJ$a7c8f3b4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2', 'normal'),
            ('prouser', 'prouser@example.com', 'pbkdf2:sha256:600000$ABC123DEF456GHI$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3', 'pro')
        ]

        cursor.executemany(
            "INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            default_users
        )

        # Create default categories for each user
        default_categories = [
            ('Food', 'bi-basket', 'success'),
            ('Transportation', 'bi-car-front', 'primary'),
            ('Entertainment', 'bi-film', 'info'),
            ('Shopping', 'bi-cart', 'warning'),
            ('Bills', 'bi-receipt', 'danger'),
            ('Salary', 'bi-cash', 'success'),
            ('Other Income', 'bi-piggy-bank', 'primary'),
            ('Uncategorized', 'bi-tag', 'secondary')
        ]

        # Add categories for each user
        for user_id in range(1, 5):  # For our 4 default users
            for name, icon, color in default_categories:
                cursor.execute(
                    "INSERT INTO category (name, icon, color, user_id) VALUES (?, ?, ?, ?)",
                    (name, icon, color, user_id)
                )

        # Commit changes
        conn.commit()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
