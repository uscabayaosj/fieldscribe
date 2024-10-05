from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from utils.decorators import admin_required
from flask_app.models import User, Entry
from flask_app.extensions import db

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@bp.route('/manage_entries')
@login_required
@admin_required
def manage_entries():
    entries = Entry.query.all()
    return render_template('admin/manage_entries.html', entries=entries)
