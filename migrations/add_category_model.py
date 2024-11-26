import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, User
from models import Category, Transaction
from datetime import datetime

def upgrade():
    # Create categories table
    if not hasattr(Category, '__table__'):
        Category.__table__.create(db.engine)
    
    # Get all existing transactions
    transactions = Transaction.query.all()
    
    # Store existing category data
    category_data = {}
    for transaction in transactions:
        category_data[transaction.id] = transaction.category
    
    # Drop the category column from transactions
    with db.engine.connect() as conn:
        conn.execute(db.text('ALTER TABLE transaction DROP COLUMN category'))
        conn.execute(db.text('ALTER TABLE transaction ADD COLUMN category_id INTEGER REFERENCES category(id)'))
    
    # Create default categories for each user
    default_categories = {
        'Food': True,
        'Transportation': True,
        'Entertainment': True,
        'Bills': True,
        'Shopping': True,
        'Salary': False,
        'Other Income': False,
        'Other Expenses': True
    }
    
    # Get all users
    users = User.query.all()
    
    # Create categories for each user
    for user in users:
        existing_categories = {}
        
        # First, create default categories
        for cat_name, is_expense in default_categories.items():
            category = Category(
                name=cat_name,
                user_id=user.id,
                created_at=datetime.utcnow()
            )
            db.session.add(category)
            existing_categories[cat_name] = category
        
        # Add any additional categories from existing transactions
        for transaction in user.transactions:
            cat_name = category_data.get(transaction.id)
            if cat_name and cat_name not in existing_categories:
                category = Category(
                    name=cat_name,
                    user_id=user.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(category)
                existing_categories[cat_name] = category
        
        db.session.commit()
        
        # Update transactions with category IDs
        for transaction in user.transactions:
            old_category = category_data.get(transaction.id)
            if old_category in existing_categories:
                transaction.category_id = existing_categories[old_category].id
        
        db.session.commit()

if __name__ == '__main__':
    upgrade()
