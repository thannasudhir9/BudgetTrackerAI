from flask import jsonify, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
from models import User, UserRole
from extensions import db, mail
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_user_routes(app):
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
