from flask import jsonify, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
from models import User, UserRole
from extensions import db, mail
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_user_routes(app):
    @app.route('/admin/users')
    @login_required
    def admin_users():
        # Check if user is admin or super admin
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Get all users
        users = User.query.order_by(User.id.desc()).all()
        return render_template('admin/users.html', users=users)

    @app.route('/api/admin/users', methods=['POST'])
    @login_required
    def create_user():
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(key in data for key in ['username', 'email', 'password', 'role']):
                return jsonify({'error': 'Missing required fields'}), 400
                
            # Check if email already exists
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already registered'}), 400
                
            # Create new user
            user = User(
                username=data['username'],
                email=data['email'],
                role=UserRole[data['role']]
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'message': 'User created successfully'}), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/admin/users/<int:user_id>', methods=['GET'])
    @login_required
    def get_user(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.name,
            'is_active': user.is_active
        })

    @app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
    @login_required
    def update_user(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            user = User.query.get_or_404(user_id)
            data = request.get_json()
            
            # Update fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'password' in data:
                user.set_password(data['password'])
            if 'role' in data:
                user.role = UserRole[data['role']]
                
            db.session.commit()
            return jsonify({'message': 'User updated successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
    @login_required
    def delete_user(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            user = User.query.get_or_404(user_id)
            
            # Don't allow deleting yourself
            if user.id == current_user.id:
                return jsonify({'error': 'Cannot delete your own account'}), 400
                
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'message': 'User deleted successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/admin/users/<int:user_id>/activate', methods=['POST'])
    @login_required
    def activate_user(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            user = User.query.get_or_404(user_id)
            user.is_active = True
            db.session.commit()
            
            return jsonify({'message': 'User activated successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/api/admin/users/<int:user_id>/deactivate', methods=['POST'])
    @login_required
    def deactivate_user(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            user = User.query.get_or_404(user_id)
            
            # Don't allow deactivating yourself
            if user.id == current_user.id:
                return jsonify({'error': 'Cannot deactivate your own account'}), 400
                
            user.is_active = False
            db.session.commit()
            
            return jsonify({'message': 'User deactivated successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @app.route('/reset_password_request', methods=['GET', 'POST'])
    def reset_password_request():
        if request.method == 'POST':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Generate token
                token = secrets.token_urlsafe(32)
                user.reset_token = token
                user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
                db.session.commit()
                
                # Send email
                reset_url = url_for('reset_password', token=token, _external=True)
                msg = Message('Password Reset Request',
                            sender=app.config['MAIL_DEFAULT_SENDER'],
                            recipients=[user.email])
                msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.
'''
                try:
                    mail.send(msg)
                    flash('Check your email for the instructions to reset your password', 'info')
                except Exception as e:
                    app.logger.error(f"Failed to send email: {str(e)}")
                    flash('Error sending email. Please try again later.', 'error')
                    
            else:
                # Don't reveal if user exists
                flash('Check your email for the instructions to reset your password', 'info')
                
            return redirect(url_for('login'))
            
        return render_template('reset_password_request.html')

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        user = User.query.filter_by(reset_token=token).first()
        
        if not user or user.reset_token_expires < datetime.utcnow():
            flash('Invalid or expired reset token', 'error')
            return redirect(url_for('login'))
            
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not password or not confirm_password:
                flash('Please fill out all fields', 'error')
                return render_template('reset_password.html')
                
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('reset_password.html')
                
            # Update password
            user.password_hash = generate_password_hash(password)
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            
            flash('Your password has been reset', 'success')
            return redirect(url_for('login'))
            
        return render_template('reset_password.html')

    @app.route('/start-pro-trial', methods=['GET'])
    @login_required
    def start_pro_trial():
        if current_user.role != UserRole.NORMAL:
            flash('You are already on a premium plan!', 'info')
            return redirect(url_for('dashboard'))

        # Set trial expiration date to 14 days from now
        trial_end_date = datetime.utcnow() + timedelta(days=14)
        current_user.trial_end_date = trial_end_date
        current_user.role = UserRole.PRO
        
        db.session.commit()
        
        flash('Welcome to Pro! Your 14-day free trial has started.', 'success')
        return redirect(url_for('dashboard'))
