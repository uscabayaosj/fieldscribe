from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required, current_user
from models import User, Entry
from __init__ import db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        abort(403)

@bp.route('/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin/dashboard.html')

@bp.route('/users')
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/entries')
def manage_entries():
    entries = Entry.query.all()
    return render_template('admin/entries.html', entries=entries)

@bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f"Admin status for {user.username} has been {'granted' if user.is_admin else 'revoked'}.", 'success')
    else:
        flash("You cannot change your own admin status.", 'error')
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user != current_user:
        try:
            # Delete all entries associated with the user
            Entry.query.filter_by(user_id=user.id).delete()
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            flash(f"User {user.username} and all their entries have been deleted.", 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user {user.id}: {str(e)}")
            flash(f"An error occurred while deleting the user. Please try again.", 'error')
    else:
        flash("You cannot delete your own account.", 'error')
    return redirect(url_for('admin.manage_users'))

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash(f"Entry '{entry.title}' has been deleted.", 'success')
    return redirect(url_for('admin.manage_entries'))
