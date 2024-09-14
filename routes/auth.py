from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from __init__ import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('auth.admin_dashboard'))
            return redirect(url_for('entries.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('entries.dashboard'))
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@bp.route('/create_admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not current_user.is_admin:
        flash('You do not have permission to create admin users.')
        return redirect(url_for('entries.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.create_admin'))
        
        new_admin = User(username=username, email=email, is_admin=True)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin user created successfully.')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('create_admin.html')
