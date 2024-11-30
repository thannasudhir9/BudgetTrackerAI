from flask import Flask
from extensions import db, login_manager, mail
from flask_migrate import Migrate
import os
import logging

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'budget_tracker.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or another email server
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'ethstk911@gmail.com'  # Your email address
    app.config['MAIL_PASSWORD'] = 'xizb nafm vzqq gnik'   # Your email password
    app.config['MAIL_DEFAULT_SENDER'] = 'ethstk911@gmail.com'
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    login_manager.login_view = 'login'
    
    # Initialize Flask-Migrate
    #migrate = Migrate(app, db)
    
    # Import and register routes
    from routes import init_routes
    init_routes(app)
    
    # Import and register user management routes
    from user_routes import init_user_routes
    init_user_routes(app)
    
    # Import models and initialize database
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))
    
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)