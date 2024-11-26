from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from extensions import db

class UserRole(Enum):
    NORMAL = 'normal'
    PRO = 'pro'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

    def can_access_feature(self, feature_name):
        """Check if user can access a specific feature based on their role"""
        feature_permissions = {
            'basic': [UserRole.NORMAL.value, UserRole.PRO.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'pro': [UserRole.PRO.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'admin': [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'super_admin': [UserRole.SUPER_ADMIN.value]
        }
        return self.value in feature_permissions.get(feature_name, [])

class TransactionCategory(Enum):
    FOOD = {'name': 'Food', 'icon': 'bi-basket', 'color': 'success'}
    TRANSPORTATION = {'name': 'Transportation', 'icon': 'bi-car-front', 'color': 'primary'}
    ENTERTAINMENT = {'name': 'Entertainment', 'icon': 'bi-film', 'color': 'info'}
    SHOPPING = {'name': 'Shopping', 'icon': 'bi-cart', 'color': 'warning'}
    BILLS = {'name': 'Bills', 'icon': 'bi-file-text', 'color': 'danger'}
    SALARY = {'name': 'Salary', 'icon': 'bi-cash', 'color': 'success'}
    OTHER_INCOME = {'name': 'Other Income', 'icon': 'bi-wallet2', 'color': 'success'}
    UNCATEGORIZED = {'name': 'Uncategorized', 'icon': 'bi-question-circle', 'color': 'secondary'}

    @classmethod
    def get_by_name(cls, name):
        for category in cls:
            if category.value['name'].lower() == name.lower():
                return category
        return cls.UNCATEGORIZED

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.NORMAL)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    transactions = db.relationship('BudgetTransaction', backref='user', lazy=True)
    
    def __init__(self, username, email, role=UserRole.NORMAL):
        self.username = username
        self.email = email
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def is_admin(self):
        return self.role in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
    
    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN.value
    
    @property
    def is_pro(self):
        return self.role in [UserRole.PRO.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]
    
    def can_access_feature(self, feature):
        """Check if user can access a specific feature based on their role"""
        feature_permissions = {
            'basic': [UserRole.NORMAL.value, UserRole.PRO.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'pro': [UserRole.PRO.value, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'admin': [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value],
            'super_admin': [UserRole.SUPER_ADMIN.value]
        }
        return self.role in feature_permissions.get(feature, [])

    def __repr__(self):
        return f'<User {self.username}>'

class BudgetTransaction(db.Model):
    __tablename__ = 'budget_transaction'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=False, default='UNCATEGORIZED')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.description} {self.amount}>'

    @property
    def category_info(self):
        category = TransactionCategory.get_by_name(self.category)
        return category.value

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'amount': float(self.amount),
            'description': self.description,
            'type': self.type,
            'category': self.category_info
        }

    def __repr__(self):
        return f'<Transaction {self.description} {self.amount}>'
