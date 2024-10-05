from flask import Flask, redirect, url_for
from flask_app.extensions import db
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Set the database URI for PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/dbname')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from flask_app.models import User
        return User.query.get(int(user_id))

    with app.app_context():
        from flask_app import models
        db.create_all()

        # Register blueprints
        from routes.entries import bp as entries_bp
        from routes.auth import bp as auth_bp
        app.register_blueprint(entries_bp)
        app.register_blueprint(auth_bp)

        @app.route('/')
        def index():
            return redirect(url_for('entries.dashboard'))

    return app
