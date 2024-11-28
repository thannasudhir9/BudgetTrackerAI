import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from datetime import datetime
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Create category table
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                icon VARCHAR(50) NOT NULL,
                color VARCHAR(20) NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        '''))

        # Create default categories for each user
        db.session.execute(text('''
            INSERT INTO category (name, icon, color, user_id)
            SELECT 'Housing', 'bi-house', 'primary', id FROM user
            UNION ALL
            SELECT 'Transportation', 'bi-car-front', 'info', id FROM user
            UNION ALL
            SELECT 'Groceries', 'bi-cart', 'success', id FROM user
            UNION ALL
            SELECT 'Healthcare', 'bi-heart-pulse', 'danger', id FROM user
            UNION ALL
            SELECT 'Entertainment', 'bi-controller', 'warning', id FROM user
            UNION ALL
            SELECT 'Other', 'bi-tag', 'secondary', id FROM user
        '''))

        # Create new transaction table with category_id
        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS budget_transaction_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description VARCHAR(200) NOT NULL,
                amount FLOAT NOT NULL,
                type VARCHAR(20) NOT NULL,
                date DATE NOT NULL,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (category_id) REFERENCES category (id)
            )
        '''))

        # Copy data from old table to new table
        db.session.execute(text('''
            INSERT INTO budget_transaction_new (
                id, description, amount, type, date, user_id, category_id, 
                created_at, updated_at
            )
            SELECT 
                t.id, t.description, t.amount, t.type, t.date, t.user_id, 
                COALESCE(
                    (SELECT id FROM category c 
                     WHERE c.name = t.category 
                     AND c.user_id = t.user_id
                     LIMIT 1),
                    (SELECT id FROM category c 
                     WHERE c.name = 'Other' 
                     AND c.user_id = t.user_id
                     LIMIT 1)
                ) as category_id,
                t.created_at,
                t.updated_at
            FROM budget_transaction t
        '''))

        # Drop old table and rename new table
        db.session.execute(text('DROP TABLE budget_transaction'))
        db.session.execute(text('ALTER TABLE budget_transaction_new RENAME TO budget_transaction'))

        # Commit all changes
        db.session.commit()

        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
