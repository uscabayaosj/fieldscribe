from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_app.models import User
from flask_app.extensions import db
import re
from urllib.parse import urlparse, urljoin
import logging

bp = Blueprint('auth', __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

def redirect_to_dashboard():
    return redirect(url_for('admin.admin_dashboard') if current_user.is_admin else url_for('entries.dashboard'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(username) < 3 or len(username) > 20 or not re.match("^[A-Za-z0-9_]+$", username):
            flash('Username must be between 3 and 20 characters and contain only letters, numbers, and underscores.', 'warning')
            return redirect(url_for('auth.register'))
        
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email format.', 'warning')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.', 'warning')
            return redirect(url_for('auth.register'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'warning')
            return redirect(url_for('auth.register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists', 'warning')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the account. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.debug("User is already authenticated")
        return redirect_to_dashboard()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logger.debug(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            logger.debug(f"User {username} logged in successfully")
            flash('Logged in successfully.', 'success')

            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                logger.debug(f"Redirecting to next page: {next_page}")
                return redirect(next_page)
            logger.debug("Redirecting to dashboard")
            return redirect_to_dashboard()
        else:
            logger.debug(f"Invalid login attempt for username: {username}")
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))