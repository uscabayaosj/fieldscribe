from flask import Flask, redirect, url_for
from flask_app.extensions import db
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_admin_user():
    from flask_app.models import User
    logger.info("Checking for admin user...")
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        logger.info("Admin user not found. Creating new admin user...")
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created successfully.")
    else:
        logger.info("Admin user already exists.")

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Set the database URI for PostgreSQL with SSL mode required
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/dbname')
    if '?sslmode=' not in app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] += '?sslmode=require'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    # Add UPLOAD_FOLDER configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from flask_app.models import User
        return User.query.get(int(user_id))

    with app.app_context():
        from flask_app import models

        # Register blueprints
        from routes.entries import bp as entries_bp
        from routes.auth import bp as auth_bp
        from routes.admin import bp as admin_bp
        app.register_blueprint(entries_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')

        @app.route('/')
        def index():
            return redirect(url_for('entries.dashboard'))

        # Ensure admin user is created
        create_admin_user()

    return app
