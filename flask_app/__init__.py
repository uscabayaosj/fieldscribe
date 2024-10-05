from flask import Flask, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_admin_user():
    from .models import User
    # Check if the admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create the admin user
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('your-admin-password')  # Ensure you have a set_password method
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created successfully.")
    else:
        logger.info("Admin user already exists.")

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Set the database URI for PostgreSQL with SSL mode disabled
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/dbname')
    if '?sslmode=' not in app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] += '?sslmode=disable'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    # Add UPLOAD_FOLDER configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    with app.app_context():
        try:
            from . import models
            db.create_all()  # This will create tables based on your models

            # Create admin user if it doesn't exist
            create_admin_user()

            # Register blueprints
            from .routes.entries import bp as entries_bp
            from .routes.auth import bp as auth_bp
            from .routes.admin import bp as admin_bp
            app.register_blueprint(entries_bp)
            app.register_blueprint(auth_bp, url_prefix='/auth')
            app.register_blueprint(admin_bp, url_prefix='/admin')

            @app.route('/')
            def index():
                return redirect(url_for('entries.dashboard'))

        except Exception as e:
            logger.error(f"An error occurred during app initialization: {str(e)}")
            raise

    return app
