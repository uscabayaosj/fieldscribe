from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from __init__ import db
import re
from urllib.parse import urlparse, urljoin

# Create a Blueprint for authentication-related routes
bp = Blueprint('auth', __name__)

def is_safe_url(target):
    # Check if the target URL is safe by comparing its scheme and netloc with the current request
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

def redirect_to_dashboard():
    # Redirect to the appropriate dashboard based on user role
    return redirect(url_for('admin.admin_dashboard') if current_user.is_admin else url_for('entries.dashboard'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Validate username length and characters
        if len(username) < 3 or len(username) > 20 or not re.match("^[A-Za-z0-9_]+$", username):
            flash('Username must be between 3 and 20 characters and contain only letters, numbers, and underscores.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash('Invalid email format.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Validate password length and complexity
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.', 'warning')
            return redirect(url_for('auth.register'))
        
        # Check if username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'warning')
            return redirect(url_for('auth.register'))

        # Check if email already exists after validating format
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists', 'warning')
            return redirect(url_for('auth.register'))
        
        # Create a new user and hash the password
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Use the set_password method
        
        # Add and commit the new user to the database
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
    # Redirect to appropriate dashboard if user is already logged in
    if current_user.is_authenticated:
        return redirect_to_dashboard()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the user exists and verify the password
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):  # Use the check_password method
            login_user(user)  # Log in the user

            # Redirect to the original page requested or to the dashboard
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect_to_dashboard()
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
# Route to log out the user
# Requires the user to be logged in
# Logs out the user and redirects to the login page
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
