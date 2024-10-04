from flask import Flask
from flask_app.extensions import db  # Import db from extensions
import os

def create_app():
    app = Flask(__name__)

    # Set the database URI for PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost/dbname')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional: Disable track modifications

    db.init_app(app)  # Initialize the db with the app

    with app.app_context():
        from flask_app import models  # Import models within the app context
        db.create_all()  # Create database tables

    return app
