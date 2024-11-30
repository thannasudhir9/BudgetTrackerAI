from flask import jsonify, flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user
from models import User, UserRole, Feedback
from extensions import db, mail
from flask_mail import Message
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import csv
from io import StringIO
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kws)
    return decorated_function

def init_user_routes(app):
    @app.route('/admin/users')
    @login_required
    @admin_required
    def admin_users():
        # Check if user is admin or super admin
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Get all users
        users = User.query.order_by(User.id.desc()).all()
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        return render_template('admin/users.html', users=users, feedbacks=feedbacks)

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
            data = request.get_json()
            user = User.query.get_or_404(user_id)
            
            # Prevent self-modification for non-super-admin
            if user.id == current_user.id and current_user.role != UserRole.SUPER_ADMIN:
                return jsonify({'error': 'Cannot modify your own account'}), 403
            
            # Update fields
            if 'username' in data:
                user.username = data['username']
            if 'email' in data:
                user.email = data['email']
            if 'role' in data:
                try:
                    user.role = UserRole[data['role']]
                except KeyError:
                    return jsonify({'error': 'Invalid role'}), 400
            if 'is_active' in data:
                user.is_active = data['is_active']
            
            db.session.commit()
            return jsonify({'message': 'User updated successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

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

    @app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
    @login_required
    def update_user_role(user_id):
        if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return jsonify({'error': 'Unauthorized'}), 403
            
        try:
            data = request.get_json()
            if 'role' not in data:
                return jsonify({'error': 'Role is required'}), 400
                
            user = User.query.get_or_404(user_id)
            
            # Prevent self-role change
            if user.id == current_user.id:
                return jsonify({'error': 'Cannot change your own role'}), 403
                
            try:
                new_role = UserRole[data['role']]
            except KeyError:
                return jsonify({'error': 'Invalid role'}), 400
                
            user.role = new_role
            db.session.commit()
            
            return jsonify({'message': 'User role updated successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

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

    def send_feedback_notification(feedback):
        """Send email notification to super admin about new feedback"""
        super_admin = User.query.filter_by(role=UserRole.SUPER_ADMIN).first()
        if not super_admin:
            return
            
        subject = f'New Feedback: {feedback.subject}'
        body = f'''
New feedback received from {feedback.name} ({feedback.email})

Subject: {feedback.subject}
User ID: {feedback.user_id if feedback.user_id else 'Not logged in'}
Message:
{feedback.message}

Submitted at: {feedback.created_at}
'''
        
        #send_email(super_admin.email, subject, body)
        #send_email('thannasudhir.de@gmail.com', subject, body)

    @app.route('/submit_feedback', methods=['POST'])
    def submit_feedback():
        try:
            # Get data from either JSON or form data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
        
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field.title()} is required'}), 400

            # Create new feedback entry
            feedback = Feedback(
                name=data['name'],
                email=data['email'],
                subject=data['subject'],
                message=data['message'],
                user_id=current_user.id if current_user.is_authenticated else None
            )
        
            # Save to database
            db.session.add(feedback)
            db.session.commit()
        
            # Send email notification to super admin
            send_feedback_notification(feedback)
        
            return jsonify({
                'success': True, 
                'message': 'Thank you for your feedback! We will get back to you soon.'
            }), 200
    
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error submitting feedback: {str(e)}")
            return jsonify({'error': 'An error occurred processing your request'}), 500

    @app.route('/admin/feedback/<int:id>')
    @login_required
    @admin_required
    def get_feedback(id):
        feedback = Feedback.query.get_or_404(id)
        return jsonify(feedback.to_dict())

    @app.route('/admin/feedback/<int:id>/toggle-read', methods=['POST'])
    @login_required
    @admin_required
    def toggle_feedback_read(id):
        feedback = Feedback.query.get_or_404(id)
        try:
            feedback.is_read = not feedback.is_read
            feedback.read_at = datetime.utcnow() if feedback.is_read else None
            db.session.commit()
            return jsonify({
                'success': True,
                'is_read': feedback.is_read,
                'read_at': feedback.read_at.strftime('%Y-%m-%d %H:%M') if feedback.read_at else None
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/admin/feedback/<int:id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_feedback(id):
        feedback = Feedback.query.get_or_404(id)
        try:
            db.session.delete(feedback)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/admin/feedback/export')
    @login_required
    @admin_required
    def export_feedback():
        format = request.args.get('format', 'csv')
        if format == 'csv':
            si = StringIO()
            cw = csv.writer(si)
            cw.writerow(['Date', 'Name', 'Email', 'Subject', 'Message', 'User'])
        
            feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
            for feedback in feedbacks:
                cw.writerow([
                    feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                    feedback.name,
                    feedback.email,
                    feedback.subject,
                    feedback.message,
                    feedback.user.username if feedback.user else 'Guest'
                ])
        
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=feedback_export.csv"
            output.headers["Content-type"] = "text/csv"
            return output
    
        return jsonify({'error': 'Unsupported format'}), 400

    @app.route('/admin/feedback/filter')
    @login_required
    @admin_required
    def filter_feedback():
        # Get filter parameters
        status = request.args.get('status')  # 'read', 'unread', or None
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        search = request.args.get('search')

        # Start with base query
        query = Feedback.query

        # Apply filters
        if status == 'read':
            query = query.filter(Feedback.is_read == True)
        elif status == 'unread':
            query = query.filter(Feedback.is_read == False)

        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Feedback.created_at >= date_from)
            except ValueError:
                pass

        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                date_to = date_to + timedelta(days=1)  # Include the entire day
                query = query.filter(Feedback.created_at < date_to)
            except ValueError:
                pass

        if search:
            search = f"%{search}%"
            query = query.filter(
                db.or_(
                    Feedback.name.ilike(search),
                    Feedback.email.ilike(search),
                    Feedback.subject.ilike(search),
                    Feedback.message.ilike(search)
                )
            )

        # Get results ordered by creation date
        feedbacks = query.order_by(Feedback.created_at.desc()).all()

        # Convert to list of dictionaries for JSON response
        feedback_list = [{
            'id': f.id,
            'name': f.name,
            'email': f.email,
            'subject': f.subject,
            'message': f.message,
            'created_at': f.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': f.is_read,
            'read_at': f.read_at.strftime('%Y-%m-%d %H:%M') if f.read_at else None,
            'user': f.user.username if f.user else 'Guest'
        } for f in feedbacks]

        return jsonify({
            'success': True,
            'feedbacks': feedback_list
        })
