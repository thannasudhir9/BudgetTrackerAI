from app import app, db
from sqlalchemy import text

def cleanup_tables(auto_confirm=True):
    with app.app_context():
        try:
            # Get list of all tables
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print("\nExisting tables:")
            for table in tables:
                if table != 'sqlite_sequence':  # Skip SQLite internal table
                    # Get row count for each table
                    count_result = db.session.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = count_result.scalar()
                    print(f"- {table} ({count} rows)")

            # Tables to keep
            essential_tables = {'user', 'budget_transaction', 'sqlite_sequence'}
            tables_to_delete = [table for table in tables if table not in essential_tables]

            if not tables_to_delete:
                print("\nNo unnecessary tables found.")
                return

            print("\nTables to be deleted:")
            for table in tables_to_delete:
                print(f"- {table}")

            if not auto_confirm:
                confirm = input("\nDo you want to proceed with deletion? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Operation cancelled.")
                    return

            # Delete unnecessary tables
            for table in tables_to_delete:
                db.session.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
                print(f"Deleted table: {table}")
            
            db.session.commit()
            print("\nCleanup completed successfully!")

        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    cleanup_tables(auto_confirm=True)
