from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum
from . import db

class UserRole(Enum):
    NORMAL = 'normal'
    PRO = 'pro'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.NORMAL, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
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

    # Role-based permissions
    @property
    def is_admin(self):
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN
    
    @property
    def is_pro(self):
        return self.role in [UserRole.PRO, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def can_access_feature(self, feature):
        """Check if user can access a specific feature based on their role"""
        feature_permissions = {
            'basic': [UserRole.NORMAL, UserRole.PRO, UserRole.ADMIN, UserRole.SUPER_ADMIN],
            'pro': [UserRole.PRO, UserRole.ADMIN, UserRole.SUPER_ADMIN],
            'admin': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
            'super_admin': [UserRole.SUPER_ADMIN]
        }
        return self.role in feature_permissions.get(feature, [])

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.description} {self.amount}>'
