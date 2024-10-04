from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Create the SQLAlchemy instance outside of the create_app function
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configure your database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'journal.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a real secret key
    
    # Initialize the app with the SQLAlchemy instance
    db.init_app(app)
    login_manager.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from .models import User
        
        # Create tables
        db.create_all()
        
        # Your existing code
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('admin123')  # Set a default password
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")

    # Update these imports to match your project structure
    from routes import auth, entries, media, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(entries.bp)
    app.register_blueprint(media.bp)
    app.register_blueprint(admin.bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
