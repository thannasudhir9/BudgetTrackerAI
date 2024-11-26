import os
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import User, UserRole, BudgetTransaction

def setup_database():
    app = create_app()
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create tables
        db.create_all()
        print("Created new tables")
        
        # Create test users
        test_users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'role': UserRole.ADMIN,
                'last_login': datetime.utcnow()
            },
            {
                'username': 'superadmin',
                'email': 'superadmin@example.com',
                'password': 'superadmin123',
                'role': UserRole.SUPER_ADMIN,
                'last_login': datetime.utcnow()
            },
            {
                'username': 'user',
                'email': 'user@example.com',
                'password': 'user123',
                'role': UserRole.NORMAL,
                'last_login': datetime.utcnow()
            },
            {
                'username': 'pro_user',
                'email': 'pro@example.com',
                'password': 'pro123',
                'role': UserRole.PRO,
                'last_login': datetime.utcnow()
            }
        ]

        # Add users
        for user_data in test_users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            user.last_login = user_data['last_login']
            user.created_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            db.session.add(user)
            print(f"Created user: {user_data['username']}")

        # Commit users first to get their IDs
        db.session.commit()

        # Create sample transactions for each user
        categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Salary', 'Other Income']
        descriptions = {
            'Food': ['Grocery shopping', 'Restaurant dinner', 'Coffee shop', 'Fast food'],
            'Transportation': ['Gas', 'Bus ticket', 'Train pass', 'Car maintenance'],
            'Entertainment': ['Movie tickets', 'Concert', 'Video games', 'Streaming service'],
            'Shopping': ['Clothes', 'Electronics', 'Home decor', 'Books'],
            'Bills': ['Electricity bill', 'Water bill', 'Internet bill', 'Phone bill'],
            'Salary': ['Monthly salary', 'Bonus', 'Overtime pay'],
            'Other Income': ['Freelance work', 'Investment returns', 'Side project']
        }

        # Now create transactions
        users = User.query.all()
        for user in users:
            # Generate 20 random transactions for each user
            for _ in range(20):
                category = random.choice(categories)
                is_income = category in ['Salary', 'Other Income']
                amount = random.uniform(10, 1000)
                if not is_income:
                    amount = -amount
                
                transaction = BudgetTransaction(
                    user_id=user.id,
                    amount=round(amount, 2),
                    description=random.choice(descriptions[category]),
                    type='income' if is_income else 'expense',
                    category=category,
                    date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(transaction)
                print(f"Created transaction for {user.username}: {transaction.description} ({transaction.amount})")

        # Commit all changes
        db.session.commit()
        print("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()
