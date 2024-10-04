from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required, current_user
from models import User, Entry
from __init__ import db
from utils.decorators import admin_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@admin_required
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/users')
@admin_required
@login_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    users = User.query.paginate(page=page, per_page=per_page)
    return render_template('admin/users.html', users=users)

@bp.route('/entries')
@admin_required
@login_required
def manage_entries():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    entries = Entry.query.paginate(page=page, per_page=per_page)
    return render_template('admin/entries.html', entries=entries)

@bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
@login_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f"Admin status for {user.username} has been {'granted' if user.is_admin else 'revoked'}.", 'success')
    else:
        flash("You cannot change your own admin status.", 'warning')
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} has been deleted.", 'success')
    else:
        flash("You cannot delete your own account.", 'warning')
    return redirect(url_for('admin.manage_users'))

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash(f"Entry '{entry.title}' has been deleted.", 'success')
    return redirect(url_for('admin.manage_entries'))
