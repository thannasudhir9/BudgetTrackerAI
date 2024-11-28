from app import app, db
from sqlalchemy import text
from datetime import datetime

def migrate_transactions():
    with app.app_context():
        try:
            # Check if the old table exists
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='transaction'"))
            if not result.scalar():
                print("Old 'transaction' table not found. No migration needed.")
                return

            # Get the structure of the old table
            result = db.session.execute(text("PRAGMA table_info('transaction')"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Existing columns in transaction table: {columns}")

            # Create the new table if it doesn't exist
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS budget_transaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description VARCHAR(200) NOT NULL,
                    amount FLOAT NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    date DATETIME NOT NULL,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            """))
            db.session.commit()

            # Build the INSERT query based on existing columns
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            select_fields = []
            insert_fields = []
            
            # Map the basic fields that should exist in both tables
            base_fields = ['id', 'description', 'amount', 'type', 'category', 'date', 'user_id']
            for field in base_fields:
                if field in columns:
                    select_fields.append(field)
                    insert_fields.append(field)

            # Add timestamps with default values if they don't exist
            if 'created_at' in columns:
                select_fields.append('created_at')
            insert_fields.append('created_at')

            if 'updated_at' in columns:
                select_fields.append('updated_at')
            insert_fields.append('updated_at')

            # Build and execute the INSERT query
            select_clause = ', '.join(select_fields)
            if 'created_at' not in columns:
                select_clause += f", '{current_time}' as created_at"
            if 'updated_at' not in columns:
                select_clause += f", '{current_time}' as updated_at"

            insert_clause = ', '.join(insert_fields)
            
            query = f"""
                INSERT INTO budget_transaction ({insert_clause})
                SELECT {select_clause}
                FROM "transaction"
            """
            print(f"\nExecuting migration query:\n{query}")
            
            db.session.execute(text(query))
            db.session.commit()

            # Get the count of migrated records
            result = db.session.execute(text("SELECT COUNT(*) FROM budget_transaction"))
            migrated_count = result.scalar()
            print(f"\nSuccessfully migrated {migrated_count} transactions to budget_transaction table")

            # Optionally, rename the old table as backup
            db.session.execute(text('ALTER TABLE "transaction" RENAME TO transaction_backup'))
            db.session.commit()
            print("Old table renamed to transaction_backup")

        except Exception as e:
            print(f"Error during migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_transactions()
