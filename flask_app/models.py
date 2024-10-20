from flask_app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user' #Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    context = db.Column(db.Text)
    detailed_observation = db.Column(db.Text, nullable=False)
    reflection = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.relationship('Tag', secondary='entry_tags', backref=db.backref('entries', lazy='dynamic'))
    media = db.relationship('Media', backref='entry', lazy='dynamic')
    share_token = db.Column(db.String(32), unique=True)
    user = db.relationship('User', backref='entries')

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

entry_tags = db.Table('entry_tags',
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.UTC))
    user = db.relationship('User', backref='analysis_results')

    def __repr__(self):
        return f'<AnalysisResult {self.id}>'
