from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import logging
from enum import Enum
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class UserRole(Enum):
    NORMAL = 'normal'
    PRO = 'pro'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.NORMAL)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can_access_feature(self, feature_name):
        return self.role.can_access_feature(feature_name)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def to_dict(self):
        total_amount = sum(t.amount for t in self.transactions if t.type == 'expense') * -1 + \
                      sum(t.amount for t in self.transactions if t.type == 'income')
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'total_amount': total_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'budget_transaction'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'date': self.date.strftime('%Y-%m-%d'),
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create database tables and initialize test data
def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        app.logger.info('Database tables created')

# Initialize database
init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User management routes
@app.route('/users')
@login_required
def users():
    if not current_user.role == UserRole.ADMIN:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/api/users/<int:user_id>')
@login_required
def get_user(user_id):
    if not current_user.role == UserRole.ADMIN:
        return jsonify({'error': 'Access denied'}), 403
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role.value,
        'is_active': user.is_active
    })

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if not current_user.role == UserRole.ADMIN:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Only super_admin can modify admin and super_admin users
    if not current_user.role == UserRole.SUPER_ADMIN and user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return jsonify({'error': 'Cannot modify admin users'}), 403

    # Prevent self-deactivation
    if user.id == current_user.id and not data.get('is_active', True):
        return jsonify({'error': 'Cannot deactivate your own account'}), 400

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    
    # Only super_admin can assign admin roles
    if current_user.role == UserRole.SUPER_ADMIN:
        user.role = UserRole(data.get('role', user.role.value))
    elif data.get('role') in ['admin', 'super_admin']:
        return jsonify({'error': 'Cannot assign admin roles'}), 403
    else:
        user.role = UserRole(data.get('role', user.role.value))

    user.is_active = data.get('is_active', user.is_active)
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not current_user.role == UserRole.ADMIN:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Only super_admin can modify admin and super_admin users
    if not current_user.role == UserRole.SUPER_ADMIN and user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return jsonify({'error': 'Cannot modify admin users'}), 403

    # Prevent self-deactivation
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot toggle your own account status'}), 400

    user.is_active = data.get('is_active', not user.is_active)
    db.session.commit()
    return jsonify({'message': 'User status updated successfully'})

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.role == UserRole.ADMIN:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Validate role assignment
    role = data.get('role', 'normal')
    if not current_user.role == UserRole.SUPER_ADMIN and role in ['admin', 'super_admin']:
        return jsonify({'error': 'Cannot create admin users'}), 403

    user = User(
        username=data['username'],
        email=data['email'],
        role=UserRole(role),
        is_active=data.get('is_active', True)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is inactive. Please contact support.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=remember)
            
            # Redirect admin users to admin dashboard
            if user.role == UserRole.ADMIN:
                return redirect(url_for('admin_dashboard'))
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.role == UserRole.ADMIN:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))

    # Get statistics for admin dashboard
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'pro_users': User.query.filter_by(role=UserRole.ADMIN).count(),
        'total_transactions': Transaction.query.count()
    }
    
    # Calculate percentages and growth
    stats['active_percentage'] = round((stats['active_users'] / stats['total_users']) * 100 if stats['total_users'] > 0 else 0)
    stats['pro_percentage'] = round((stats['pro_users'] / stats['total_users']) * 100 if stats['total_users'] > 0 else 0)
    
    # Mock growth data (replace with actual calculations in production)
    stats['user_growth'] = 15
    stats['transaction_growth'] = 23

    # Get recent activity (mock data - implement actual logging in production)
    recent_activity = [
        {'user': 'john_doe', 'action': 'Created account', 'details': 'New user registration', 'time': '2 hours ago'},
        {'user': 'jane_smith', 'action': 'Added transaction', 'details': 'Expense: Groceries $150', 'time': '3 hours ago'},
        {'user': 'admin', 'action': 'Updated user', 'details': 'Modified user role', 'time': '4 hours ago'}
    ]

    # Get new users
    new_users = User.query.order_by(User.id.desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_activity=recent_activity,
                         new_users=new_users)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Here you would typically send a password reset email
            flash('Password reset instructions have been sent to your email')
            return redirect(url_for('login'))
        
        flash('Email not found')
    return render_template('forgot_password.html')

@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'icon': c.icon,
            'color': c.color,
            'total_amount': sum(t.amount for t in Transaction.query.filter_by(category_id=c.id).all())
        } for c in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    try:
        data = request.get_json()
        if not all(k in data for k in ('name', 'icon', 'color')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        category = Category(
            name=data['name'],
            icon=data['icon'],
            color=data['color']
        )
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'color': category.color,
            'total_amount': 0
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if not all(k in data for k in ('name', 'icon', 'color')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        category.name = data['name']
        category.icon = data['icon']
        category.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'color': category.color,
            'total_amount': sum(t.amount for t in Transaction.query.filter_by(category_id=category.id).all())
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    try:
        app.logger.info('Fetching transactions for user %s', current_user.id)
        period = request.args.get('period', 'all')
        app.logger.debug('Period filter: %s', period)
        
        # Base query
        query = Transaction.query.filter_by(user_id=current_user.id)
        
        # Apply period filter if specified
        if period != 'all':
            today = datetime.now().date()
            if period == 'week':
                start_date = today - timedelta(days=7)
            elif period == 'month':
                start_date = today.replace(day=1)
            elif period == 'year':
                start_date = today.replace(month=1, day=1)
            
            query = query.filter(Transaction.date >= start_date)
            app.logger.debug('Filtered by date >= %s', start_date)
        
        # Execute query and sort by date
        transactions = query.order_by(Transaction.date.desc()).all()
        app.logger.info('Found %d transactions', len(transactions))
        
        # Format response
        response = [{
            'id': t.id,
            'description': t.description,
            'amount': float(t.amount),  # Ensure amount is float
            'date': t.date.isoformat() if isinstance(t.date, datetime) else t.date,
            'category': {
                'id': t.category.id,
                'name': t.category.name,
                'icon': t.category.icon,
                'color': t.category.color
            } if t.category else None
        } for t in transactions]
        
        app.logger.debug('Returning response: %s', response)
        return jsonify(response)
    except Exception as e:
        app.logger.error('Error fetching transactions: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
@login_required
def add_transaction():
    try:
        app.logger.info('Adding new transaction for user %s', current_user.id)
        data = request.get_json()
        app.logger.debug('Received data: %s', data)
        
        if not all(k in data for k in ('description', 'amount', 'date', 'category_id')):
            missing = [k for k in ('description', 'amount', 'date', 'category_id') if k not in data]
            app.logger.warning('Missing required fields: %s', missing)
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        
        # Convert amount to negative if it's an expense
        amount = float(data['amount'])
        if data.get('type', 'expense') == 'expense':
            amount = -abs(amount)
        else:
            amount = abs(amount)
        
        # Validate category exists
        category = Category.query.get(data['category_id'])
        if not category:
            app.logger.warning('Invalid category_id: %s', data['category_id'])
            return jsonify({'error': 'Invalid category'}), 400
        
        transaction = Transaction(
            description=data['description'],
            amount=amount,
            date=datetime.fromisoformat(data['date']),
            category_id=data['category_id'],
            user_id=current_user.id,
            type=data.get('type', 'expense')
        )
        
        db.session.add(transaction)
        db.session.commit()
        app.logger.info('Transaction added successfully: %s', transaction.id)
        
        return jsonify({
            'id': transaction.id,
            'description': transaction.description,
            'amount': float(transaction.amount),
            'date': transaction.date.isoformat(),
            'category': {
                'id': transaction.category.id,
                'name': transaction.category.name,
                'icon': transaction.category.icon,
                'color': transaction.category.color
            }
        })
    except ValueError as e:
        app.logger.error('Validation error: %s', str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error('Error adding transaction: %s', str(e))
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': transaction.id,
        'description': transaction.description,
        'amount': abs(transaction.amount),
        'type': 'income' if transaction.amount > 0 else 'expense',
        'date': transaction.date.strftime('%Y-%m-%d'),
        'category_id': transaction.category_id
    })

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # Ensure user owns the transaction
        if transaction.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if not all(k in data for k in ('description', 'amount', 'date', 'category_id')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Convert amount to negative if it's an expense
        amount = float(data['amount'])
        if data.get('type', 'expense') == 'expense':
            amount = -abs(amount)
        else:
            amount = abs(amount)
        
        transaction.description = data['description']
        transaction.amount = amount
        transaction.date = datetime.fromisoformat(data['date'])
        transaction.category_id = data['category_id']
        
        db.session.commit()
        
        return jsonify({
            'id': transaction.id,
            'description': transaction.description,
            'amount': float(transaction.amount),
            'date': transaction.date.isoformat(),
            'category': {
                'id': transaction.category.id,
                'name': transaction.category.name,
                'icon': transaction.category.icon,
                'color': transaction.category.color
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        
        # Ensure user owns the transaction
        if transaction.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/transactions/summary', methods=['GET'])
@login_required
def get_transaction_summary():
    try:
        # Get all transactions for the current user
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.asc()).all()
        
        if not transactions:
            return jsonify({
                'success': True,
                'data': {
                    'months': [],
                    'incomes': [],
                    'expenses': [],
                    'categories': {'labels': [], 'values': []},
                    'summary': {'total_income': 0, 'total_expenses': 0, 'balance': 0}
                }
            })
        
        # Initialize data structures
        monthly_data = {}
        categories = {}
        total_income = 0
        total_expenses = 0
        
        # Process transactions
        for transaction in transactions:
            # Format month for consistency
            month_key = transaction.date.strftime('%Y-%m')
            month_label = transaction.date.strftime('%b %Y')
            
            # Initialize month data if not exists
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'label': month_label,
                    'income': 0,
                    'expenses': 0
                }
            
            # Update monthly totals
            amount = float(transaction.amount)
            if transaction.type == 'income':
                monthly_data[month_key]['income'] += amount
                total_income += amount
            else:  # expense
                monthly_data[month_key]['expenses'] += amount
                total_expenses += amount
                # Update category totals (only for expenses)
                if transaction.category.name not in categories:
                    categories[transaction.category.name] = 0
                categories[transaction.category.name] += amount
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        
        # Prepare final data structure
        chart_data = {
            'months': [monthly_data[month]['label'] for month in sorted_months],
            'incomes': [monthly_data[month]['income'] for month in sorted_months],
            'expenses': [monthly_data[month]['expenses'] for month in sorted_months],
            'categories': {
                'labels': list(categories.keys()),
                'values': list(categories.values())
            },
            'summary': {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'balance': total_income - total_expenses
            }
        }
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
    except Exception as e:
        app.logger.error(f'Error generating summary: {str(e)}')
        return jsonify({'success': False, 'error': 'Failed to generate summary'}), 500

@app.route('/api/dashboard/summary')
@login_required
def get_dashboard_summary():
    try:
        # Get current date and start of current month
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all transactions for the current month
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_of_month
        ).all()
        
        # Calculate monthly totals
        monthly_income = sum(t.amount for t in transactions if t.type == 'income')
        monthly_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        
        # Get all transactions for total balance
        all_transactions = Transaction.query.filter_by(user_id=current_user.id).all()
        total_balance = sum(t.amount if t.type == 'income' else -t.amount for t in all_transactions)
        
        # Calculate savings rate
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
        
        # Get category data
        categories = Category.query.all()
        category_data = []
        for category in categories:
            total = sum(-t.amount if t.type == 'expense' else t.amount for t in category.transactions)
            if total != 0:  # Only include categories with transactions
                category_data.append({
                    'name': category.name,
                    'amount': abs(total)  # Use absolute value for chart
                })
        
        # Get trend data (last 6 months)
        trend_data = {'labels': [], 'income': [], 'expenses': []}
        for i in range(5, -1, -1):
            date = now - relativedelta(months=i)
            start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + relativedelta(months=1)).replace(microsecond=0) - timedelta(seconds=1)
            
            month_transactions = Transaction.query.filter(
                Transaction.user_id == current_user.id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).all()
            
            trend_data['labels'].append(date.strftime('%b %Y'))
            trend_data['income'].append(sum(t.amount for t in month_transactions if t.type == 'income'))
            trend_data['expenses'].append(sum(t.amount for t in month_transactions if t.type == 'expense'))
        
        return jsonify({
            'total_balance': total_balance,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'savings_rate': savings_rate,
            'category_data': category_data,
            'trend_data': trend_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/transactions')
@login_required
def view_transactions():
    return render_template('transactions.html')

# One-time upgrade route for existing users
@app.route('/admin/upgrade-users', methods=['POST'])
@login_required
def upgrade_existing_users():
    if not current_user.role == UserRole.ADMIN:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Update all existing users to have NORMAL role and active status
        users = User.query.all()
        updated_count = 0
        
        for user in users:
            if user.role is None:
                user.role = UserRole.NORMAL
            if user.is_active is None:
                user.is_active = True
            updated_count += 1
        
        # Make the first user a super admin if no admin exists
        admin_exists = User.query.filter(User.role == UserRole.SUPER_ADMIN).first()
        if not admin_exists and users:
            first_user = users[0]
            first_user.role = UserRole.SUPER_ADMIN
            flash(f'User {first_user.username} has been upgraded to Super Admin', 'success')
        
        db.session.commit()
        flash(f'Successfully updated {updated_count} users', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating users: {str(e)}', 'danger')
    
    return redirect(url_for('users'))

if __name__ == '__main__':
    app.run(debug=True)
