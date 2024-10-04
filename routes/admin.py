from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app
from flask_login import login_required, current_user
from models import User, Entry
from __init__ import db
from utils.decorators import admin_required  # Import the admin_required decorator from a utility module
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Create a Blueprint for the admin routes
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@admin_required
@login_required
# Route for the admin dashboard
# Requires the user to be logged in and have admin privileges
# Renders the admin dashboard template
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/users')
@admin_required
@login_required
# Route to manage users
# Requires the user to be logged in and have admin privileges
# Supports pagination with configurable items per page
# Renders the user management template with the list of users
def manage_users():
    page = request.args.get('page', 1, type=int)  # Get the current page from the request arguments, default to 1
    per_page = request.args.get('per_page', 10, type=int)  # Get the items per page from the request arguments, default to 10
    if page < 1:
        page = 1  # Ensure the page number is not less than 1
    if per_page < 1:
        per_page = 10  # Ensure the items per page is not less than 1
    users = User.query.paginate(page=page, per_page=per_page)  # Paginate the list of users
    return render_template('admin/users.html', users=users)

@bp.route('/entries')
@admin_required
@login_required
# Route to manage entries
# Requires the user to be logged in and have admin privileges
# Supports pagination with configurable items per page
# Renders the entry management template with the list of entries
def manage_entries():
    page = request.args.get('page', 1, type=int)  # Get the current page from the request arguments, default to 1
    per_page = request.args.get('per_page', 10, type=int)  # Get the items per page from the request arguments, default to 10
    if page < 1:
        page = 1  # Ensure the page number is not less than 1
    if per_page < 1:
        per_page = 10  # Ensure the items per page is not less than 1
    entries = Entry.query.paginate(page=page, per_page=per_page)  # Paginate the list of entries
    return render_template('admin/entries.html', entries=entries)

@bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
@login_required
# Route to toggle admin status for a user
# Requires the user to be logged in and have admin privileges
# Only allows toggling admin status for other users
# Handles database errors with specific error messages
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)  # Get the user by ID or return 404 if not found
    if user != current_user:
        try:
            user.is_admin = not user.is_admin  # Toggle the admin status
            db.session.commit()  # Commit the change to the database
            flash(f"Admin status for {user.username} has been {'granted' if user.is_admin else 'revoked'}.", 'success')
        except IntegrityError as e:
            db.session.rollback()  # Rollback the session in case of an integrity error
            current_app.logger.error(f"Integrity error toggling admin status for user {user.id}: {str(e)}")
            flash("A database integrity error occurred while toggling admin status. Please try again.", 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the session in case of a general SQLAlchemy error
            current_app.logger.error(f"Database error toggling admin status for user {user.id}: {str(e)}")
            flash("An unexpected database error occurred while toggling admin status. Please try again.", 'danger')
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of an unknown error
            current_app.logger.error(f"Error toggling admin status for user {user.id}: {str(e)}")
            flash("An error occurred while toggling admin status. Please try again.", 'danger')
    else:
        flash("You cannot change your own admin status.", 'warning')  # Prevent the user from changing their own admin status
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
@login_required
# Route to delete a user
# Requires the user to be logged in and have admin privileges
# Only allows deleting other users, with a confirmation step
# Handles database errors with specific error messages
def delete_user(user_id):
    user = User.query.get_or_404(user_id)  # Get the user by ID or return 404 if not found
    if user != current_user:
        try:
            # Delete all entries associated with the user after confirmation
            if request.form.get('confirm') == 'yes':
                Entry.query.filter_by(user_id=user.id).delete()  # Delete all entries related to the user
                db.session.delete(user)  # Delete the user
                db.session.commit()  # Commit the changes to the database
                flash(f"User {user.username} and all their entries have been deleted.", 'success')
            else:
                flash("User deletion not confirmed.", 'warning')  # Show a message if deletion was not confirmed
        except IntegrityError as e:
            db.session.rollback()  # Rollback the session in case of an integrity error
            current_app.logger.error(f"Integrity error deleting user {user.id}: {str(e)}")
            flash("A database integrity error occurred while deleting the user. Please try again.", 'danger')
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback the session in case of a general SQLAlchemy error
            current_app.logger.error(f"Database error deleting user {user.id}: {str(e)}")
            flash("An unexpected database error occurred while deleting the user. Please try again.", 'danger')
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of an unknown error
            current_app.logger.error(f"Error deleting user {user.id}: {str(e)}")
            flash("An error occurred while deleting the user. Please try again.", 'danger')
    else:
        flash("You cannot delete your own account.", 'warning')  # Prevent the user from deleting their own account
    return redirect(url_for('admin.manage_users'))

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@admin_required
@login_required
# Route to delete an entry
# Requires the user to be logged in and have admin privileges
# Handles database errors with specific error messages
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)  # Get the entry by ID or return 404 if not found
    try:
        db.session.delete(entry)  # Delete the entry
        db.session.commit()  # Commit the changes to the database
        flash(f"Entry '{entry.title}' has been deleted.", 'success')
    except IntegrityError as e:
        db.session.rollback()  # Rollback the session in case of an integrity error
        current_app.logger.error(f"Integrity error deleting entry {entry.id}: {str(e)}")
        flash("A database integrity error occurred while deleting the entry. Please try again.", 'danger')
    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the session in case of a general SQLAlchemy error
        current_app.logger.error(f"Database error deleting entry {entry.id}: {str(e)}")
        flash("An unexpected database error occurred while deleting the entry. Please try again.", 'danger')
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of an unknown error
        current_app.logger.error(f"Error deleting entry {entry.id}: {str(e)}")
        flash("An error occurred while deleting the entry. Please try again.", 'danger')
    return redirect(url_for('admin.manage_entries'))
