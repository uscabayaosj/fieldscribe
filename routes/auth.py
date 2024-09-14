from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
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
            return redirect(url_for('entries.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
