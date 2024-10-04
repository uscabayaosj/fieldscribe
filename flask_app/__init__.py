from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_app.models import User  # use the correct directory name here

# Create the SQLAlchemy instance outside of the create_app function
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure your database URI here
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the app with the extension
    db.init_app(app)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from .models import User
        
        # Create tables
        db.create_all()
        
        # Check for admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create admin user if not exists
            admin_user = User(username='admin', email='admin@example.com')
            admin_user.set_password('admin_password')  # Assuming you have a set_password method
            db.session.add(admin_user)
            db.session.commit()
    
    # Register blueprints or routes here
    
    return app
