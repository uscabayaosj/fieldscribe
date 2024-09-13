from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import sqlalchemy as sa

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from models import User
        db.create_all()
        # Check if the timestamp column exists in the entry table
        inspector = sa.inspect(db.engine)
        if 'timestamp' not in [c['name'] for c in inspector.get_columns('entry')]:
            # If it doesn't exist, add it
            with db.engine.connect() as connection:
                connection.execute(sa.text('ALTER TABLE entry ADD COLUMN timestamp DATETIME'))

    from routes import auth, entries, media
    app.register_blueprint(auth.bp)
    app.register_blueprint(entries.bp)
    app.register_blueprint(media.bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
