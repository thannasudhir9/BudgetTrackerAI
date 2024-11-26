from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import io
from enum import Enum
from models import User, BudgetTransaction, UserRole, TransactionCategory
from extensions import db
from sqlalchemy import desc

def init_routes(app):
    # Dashboard Route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get current date and calculate date ranges
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)

        # Daily transactions (last 7 days)
        daily_data = []
        daily_transactions = []  # List to store daily transactions
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())

            # Get transactions for this day
            day_transactions = BudgetTransaction.query.filter(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.date.between(start_of_day, end_of_day)
            ).order_by(BudgetTransaction.date.desc()).all()
            daily_transactions.extend(day_transactions)
            
            # Calculate daily totals
            income = sum(t.amount for t in day_transactions if t.amount > 0)
            expenses = abs(sum(t.amount for t in day_transactions if t.amount < 0))
            
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'income': float(income),
                'expenses': float(expenses)
            })

        # Weekly transactions (last 4 weeks)
        weekly_data = []
        weekly_transactions = []  # List to store weekly transactions
        
        for i in range(3, -1, -1):
            week_end = start_of_week - timedelta(days=i*7)
            week_start = week_end - timedelta(days=6)
            
            # Get transactions for this week
            week_transactions = BudgetTransaction.query.filter(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.date.between(
                    datetime.combine(week_start, datetime.min.time()),
                    datetime.combine(week_end, datetime.max.time())
                )
            ).order_by(BudgetTransaction.date.desc()).all()
            weekly_transactions.extend(week_transactions)
            
            # Calculate weekly totals
            income = sum(t.amount for t in week_transactions if t.amount > 0)
            expenses = abs(sum(t.amount for t in week_transactions if t.amount < 0))
            
            weekly_data.append({
                'week': f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
                'income': float(income),
                'expenses': float(expenses)
            })

        # Monthly transactions (last 6 months)
        monthly_data = []
        monthly_transactions = []  # List to store monthly transactions
        
        for i in range(5, -1, -1):
            month_start = (today - timedelta(days=30*i)).replace(day=1)
            if i > 0:
                month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            else:
                month_end = today
                
            # Get transactions for this month
            month_transactions = BudgetTransaction.query.filter(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.date.between(
                    datetime.combine(month_start, datetime.min.time()),
                    datetime.combine(month_end, datetime.max.time())
                )
            ).order_by(BudgetTransaction.date.desc()).all()
            monthly_transactions.extend(month_transactions)
            
            # Calculate monthly totals
            income = sum(t.amount for t in month_transactions if t.amount > 0)
            expenses = abs(sum(t.amount for t in month_transactions if t.amount < 0))
            
            monthly_data.append({
                'month': month_start.strftime('%B %Y'),
                'income': float(income),
                'expenses': float(expenses)
            })

        # Yearly transactions (last 3 years)
        yearly_data = []
        yearly_transactions = []  # List to store yearly transactions
        
        for i in range(2, -1, -1):
            year = today.year - i
            year_start = datetime(year, 1, 1).date()
            year_end = datetime(year, 12, 31).date() if i > 0 else today
            
            # Get transactions for this year
            year_transactions = BudgetTransaction.query.filter(
                BudgetTransaction.user_id == current_user.id,
                BudgetTransaction.date.between(
                    datetime.combine(year_start, datetime.min.time()),
                    datetime.combine(year_end, datetime.max.time())
                )
            ).order_by(BudgetTransaction.date.desc()).all()
            yearly_transactions.extend(year_transactions)
            
            # Calculate yearly totals
            income = sum(t.amount for t in year_transactions if t.amount > 0)
            expenses = abs(sum(t.amount for t in year_transactions if t.amount < 0))
            
            yearly_data.append({
                'year': str(year),
                'income': float(income),
                'expenses': float(expenses)
            })

        # Get category summary
        category_summary = db.session.query(
            BudgetTransaction.category,
            func.sum(BudgetTransaction.amount).label('total')
        ).filter(
            BudgetTransaction.user_id == current_user.id,
            BudgetTransaction.date >= start_of_month
        ).group_by(BudgetTransaction.category).all()

        # Get recent transactions
        recent_transactions = BudgetTransaction.query.filter_by(
            user_id=current_user.id
        ).order_by(
            desc(BudgetTransaction.date)
        ).limit(5).all()

        return render_template('dashboard.html',
                           daily_data=daily_data,
                           weekly_data=weekly_data,
                           monthly_data=monthly_data,
                           yearly_data=yearly_data,
                           category_summary=category_summary,
                           recent_transactions=recent_transactions,
                           daily_transactions=daily_transactions,
                           weekly_transactions=weekly_transactions,
                           monthly_transactions=monthly_transactions,
                           yearly_transactions=yearly_transactions)

    # Home Route
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('home.html')

    # Pricing Route
    @app.route('/pricing')
    def pricing():
        return render_template('pricing.html')

    # About Route
    @app.route('/about')
    def about():
        return render_template('about.html')

    # Register Route
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

    # Login Route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            login_id = request.form.get('login_id')  # Can be either username or email
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            # Try to find user by username or email
            user = User.query.filter(
                (User.username == login_id) | (User.email == login_id)
            ).first()

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
            
            flash('Invalid username/email or password', 'danger')
        
        return render_template('login.html')

    # Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    # Admin Dashboard Route
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
            'total_transactions': BudgetTransaction.query.count()
        }
        
        # Calculate percentages
        stats['active_percentage'] = round((stats['active_users'] / stats['total_users']) * 100 if stats['total_users'] > 0 else 0)
        stats['pro_percentage'] = round((stats['pro_users'] / stats['total_users']) * 100 if stats['total_users'] > 0 else 0)
        
        # Mock growth data
        stats['user_growth'] = 15
        stats['transaction_growth'] = 23

        # Get recent activity
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

    # API Routes
    @app.route('/api/categories', methods=['GET'])
    @login_required
    def get_categories():
        categories = [category.value for category in TransactionCategory]
        return jsonify(categories)

    @app.route('/api/transactions', methods=['GET'])
    @login_required
    def get_transactions():
        period = request.args.get('period', 'month')  # Default to month view
        query = BudgetTransaction.query.filter_by(user_id=current_user.id)
        
        if period != 'all':
            today = datetime.now()
            if period == 'week':
                start_date = today - timedelta(days=7)
            elif period == 'month':
                start_date = today - timedelta(days=30)
            elif period == 'year':
                start_date = today - timedelta(days=365)
            query = query.filter(BudgetTransaction.date >= start_date)
        
        transactions = query.order_by(BudgetTransaction.date.desc()).all()
        return jsonify([{
            'id': t.id,
            'date': t.date.strftime('%Y-%m-%d'),
            'amount': float(t.amount),
            'description': t.description,
            'type': t.type,
            'category': t.category_info
        } for t in transactions])

    @app.route('/api/transactions', methods=['POST'])
    @login_required
    def add_transaction():
        data = request.get_json()
        
        # Create new transaction
        transaction = BudgetTransaction(
            user_id=current_user.id,
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            description=data['description'],
            amount=float(data['amount']),
            category=data['category'],
            type='income' if float(data['amount']) > 0 else 'expense'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction added successfully'}), 201

    @app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
    @login_required
    def delete_transaction(transaction_id):
        transaction = BudgetTransaction.query.get_or_404(transaction_id)
        
        # Check if the transaction belongs to the current user
        if transaction.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200

    @app.route('/api/transactions/import', methods=['POST'])
    @login_required
    def import_transactions():
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'File must be a CSV'}), 400
        
        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            for row in csv_reader:
                # Create transaction from CSV row
                transaction = BudgetTransaction(
                    user_id=current_user.id,
                    date=datetime.strptime(row['Date'], '%Y-%m-%d'),
                    description=row['Description'],
                    amount=float(row['Amount']),
                    category=row['Category'],
                    type='income' if float(row['Amount']) > 0 else 'expense'
                )
                db.session.add(transaction)
            
            db.session.commit()
            return jsonify({'message': 'Transactions imported successfully'}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/transactions/export')
    @login_required
    def export_transactions():
        # Get all transactions for the current user
        transactions = BudgetTransaction.query\
            .filter_by(user_id=current_user.id)\
            .order_by(BudgetTransaction.date.desc())\
            .all()
        
        # Create CSV in memory
        si = io.StringIO()
        cw = csv.writer(si)
        
        # Write header
        cw.writerow(['Date', 'Description', 'Amount', 'Type', 'Category'])
        
        # Write transactions
        for transaction in transactions:
            cw.writerow([
                transaction.date.strftime('%Y-%m-%d'),
                transaction.description,
                transaction.amount,
                transaction.type,
                transaction.category
            ])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=transactions.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output

    @app.route('/api/transactions/delete-all', methods=['DELETE'])
    @login_required
    def delete_all_transactions():
        try:
            # Delete all transactions for the current user
            BudgetTransaction.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            return jsonify({'message': 'All transactions deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    # Transaction Routes
    @app.route('/transactions')
    @login_required
    def view_transactions():
        # Get filter parameters
        date_range = request.args.get('dateRange', 'all')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        transaction_type = request.args.get('type', 'all')
        category = request.args.get('category', 'all')

        # Base query
        query = BudgetTransaction.query.filter_by(user_id=current_user.id)

        # Apply date filter
        today = datetime.now().date()
        if date_range == 'today':
            query = query.filter(BudgetTransaction.date >= datetime.combine(today, datetime.min.time()))
        elif date_range == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            query = query.filter(BudgetTransaction.date >= datetime.combine(start_of_week, datetime.min.time()))
        elif date_range == 'month':
            start_of_month = today.replace(day=1)
            query = query.filter(BudgetTransaction.date >= datetime.combine(start_of_month, datetime.min.time()))
        elif date_range == 'year':
            start_of_year = today.replace(month=1, day=1)
            query = query.filter(BudgetTransaction.date >= datetime.combine(start_of_year, datetime.min.time()))
        elif date_range == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(BudgetTransaction.date.between(start, end))

        # Apply type filter
        if transaction_type == 'income':
            query = query.filter(BudgetTransaction.amount > 0)
        elif transaction_type == 'expense':
            query = query.filter(BudgetTransaction.amount < 0)

        # Apply category filter
        if category != 'all':
            query = query.filter(BudgetTransaction.category == category)

        # Get transactions with filters applied
        transactions = query.order_by(BudgetTransaction.date.desc()).all()

        # Calculate totals from filtered transactions
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        total_balance = total_income - total_expenses

        # Get categories for dropdowns
        categories = [{'name': category.name, 'value': category.value} for category in TransactionCategory]

        return render_template('transactions.html',
                           transactions=transactions,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           total_balance=total_balance,
                           categories=categories,
                           filters={
                               'dateRange': date_range,
                               'startDate': start_date,
                               'endDate': end_date,
                               'type': transaction_type,
                               'category': category
                           })

    @app.route('/download_sample_csv')
    def download_sample_csv():
        # Create sample CSV data
        sample_data = [
            ['Date', 'Description', 'Amount', 'Type', 'Category'],
            ['2024-01-17', 'Grocery Shopping', '-125.50', 'expense', 'Food'],
            ['2024-01-17', 'Monthly Salary', '5000.00', 'income', 'Salary'],
            ['2024-01-17', 'Bus Ticket', '-25.00', 'expense', 'Transportation'],
            ['2024-01-17', 'Freelance Work', '500.00', 'income', 'Other Income']
        ]
        
        # Create a string buffer to write CSV data
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(sample_data)
        
        # Create the output as bytes
        output = io.BytesIO()
        output.write(si.getvalue().encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='sample_transactions.csv'
        )

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
