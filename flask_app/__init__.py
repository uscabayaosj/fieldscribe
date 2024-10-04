from flask import Flask
from flask_app.extensions import db  # Import db from extensions

def create_app():
    app = Flask(__name__)
    # ... your existing configurations ...

    db.init_app(app)  # Initialize the db with the app

    with app.app_context():
        from flask_app import models  # Import models within the app context
        db.create_all()  # Create database tables

    return app
