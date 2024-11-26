from flask import jsonify, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
from models import User, UserRole
from extensions import db

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
