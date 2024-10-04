from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, abort, current_app
from flask_login import login_required, current_user
from models import Entry, Tag, Media
from __init__ import db
from utils.pdf_generator import generate_pdf
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid

# Create a Blueprint for entries-related routes
bp = Blueprint('entries', __name__)

@bp.route('/dashboard')
@login_required
# Route to display the user dashboard with all entries
# Requires the user to be logged in
# Queries all entries for the current user and renders the dashboard template
def dashboard():
    entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).all()
    return render_template('dashboard.html', entries=entries)

@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
# Route to create a new entry
# Requires the user to be logged in
# Handles both GET (form rendering) and POST (form submission) methods
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        location = request.form['location']
        tags = request.form.getlist('tags')

        # Create a new entry object and set the timestamp
        entry = Entry(title=title, content=content, location=location, user_id=current_user.id)
        entry.timestamp = datetime.utcnow()

        # Associate tags with the entry
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            entry.tags.append(tag)

        # Handle photo upload if present
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                try:
                    filename = secure_filename(photo.filename)  # Secure the filename
                    unique_filename = f"{uuid.uuid4().hex}_{filename[:50]}"  # Create a unique filename with a limit on length
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_dir, mode=0o755, exist_ok=True)  # Ensure the upload directory exists with proper permissions
                    photo_path = os.path.join(upload_dir, unique_filename)
                    photo.save(photo_path)  # Save the uploaded photo
                    media = Media(filename=unique_filename, media_type='image', entry=entry)
                    db.session.add(media)
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while uploading the photo. Please try again.', 'danger')
                    current_app.logger.error(f"Error uploading photo: {str(e)}")
                    return redirect(url_for('entries.new_entry'))

        # Add and commit the new entry to the database
        try:
            db.session.add(entry)
            db.session.commit()
            flash('New entry created successfully!', 'success')
            return redirect(url_for('entries.view_entry', id=entry.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the entry. Please try again.', 'danger')
            current_app.logger.error(f"Error creating new entry: {str(e)}")
            return redirect(url_for('entries.new_entry'))

    return render_template('entry_form.html')

@bp.route('/entry/<int:id>/edit', methods=['GET', 'POST'])
@login_required
# Route to edit an existing entry
# Requires the user to be logged in
# Handles both GET (form rendering) and POST (form submission) methods
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)  # Ensure the user owns the entry

    if request.method == 'POST':
        entry.title = request.form['title']
        entry.content = request.form['content']
        entry.location = request.form['location']
        tags = request.form.getlist('tags')

        # Update tags more efficiently
        current_tags = {tag.name for tag in entry.tags}
        new_tags = set(tags)

        # Add new tags that are not already associated
        for tag_name in new_tags - current_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            entry.tags.append(tag)

        # Remove tags that are no longer needed
        for tag_name in current_tags - new_tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag in entry.tags:
                entry.tags.remove(tag)

        # Handle photo upload if present
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                try:
                    filename = secure_filename(photo.filename)  # Secure the filename
                    unique_filename = f"{uuid.uuid4().hex}_{filename[:50]}"  # Create a unique filename with a limit on length
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_dir, mode=0o755, exist_ok=True)  # Ensure the upload directory exists with proper permissions
                    photo_path = os.path.join(upload_dir, unique_filename)
                    photo.save(photo_path)  # Save the uploaded photo
                    media = Media(filename=unique_filename, media_type='image', entry=entry)
                    db.session.add(media)
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while uploading the photo. Please try again.', 'danger')
                    current_app.logger.error(f"Error uploading photo during edit: {str(e)}")
                    return redirect(url_for('entries.edit_entry', id=entry.id))

        # Commit the changes to the database
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Entry updated successfully!', 'success')
            return redirect(url_for('entries.view_entry', id=entry.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the entry. Please try again.', 'danger')
            current_app.logger.error(f"Error updating entry {id}: {str(e)}")
            return redirect(url_for('entries.edit_entry', id=entry.id))

    return render_template('entry_form.html', entry=entry)

@bp.route('/entry/<int:id>/delete', methods=['POST'])
@login_required
# Route to delete an existing entry
# Requires the user to be logged in and own the entry
# Handles the deletion of the entry and commits changes to the database
def delete_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)  # Ensure the user owns the entry

    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Entry deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the entry. Please try again.', 'danger')
        current_app.logger.error(f"Error deleting entry {id}: {str(e)}")

    return redirect(url_for('entries.dashboard'))

@bp.route('/entry/<int:id>/export')
@login_required
# Route to export an entry as a PDF
# Requires the user to be logged in and own the entry
# Generates a PDF file from the entry content and sends it to the user
# Adds specific error handling for PDF generation
def export_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)  # Ensure the user owns the entry

    try:
        user_timezone = request.args.get('timezone', 'UTC')  # Get the user's timezone if provided
        pdf_content = generate_pdf(entry, user_timezone)  # Generate the PDF content
        return pdf_content, 200, {'Content-Type': 'application/pdf'}
    except IOError as e:
        current_app.logger.error(f"I/O error generating PDF for entry {id}: {str(e)}")
        flash('An I/O error occurred while generating the PDF. Please try again later.', 'danger')
    except ValueError as e:
        current_app.logger.error(f"Value error generating PDF for entry {id}: {str(e)}")
        flash('Invalid data encountered while generating the PDF. Please check your entry content.', 'danger')
    except Exception as e:
        current_app.logger.error(f"Unexpected error generating PDF for entry {id}: {str(e)}")
        flash('An error occurred while generating the PDF. Please try again later.', 'danger')
    return redirect(url_for('entries.view_entry', id=entry.id))

@bp.route('/entry/<int:id>/share', methods=['POST'])
@login_required
# Route to share an entry by generating a shareable link
# Requires the user to be logged in and own the entry
# Generates a shareable URL for the entry and returns it as a JSON response
def share_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)  # Ensure the user owns the entry

    share_url = url_for('entries.view_entry', id=entry.id, _external=True)  # Generate the shareable URL
    return jsonify({'share_url': share_url})

@bp.errorhandler(403)
# Error handler for 403 Forbidden errors
# Flashes an error message and redirects the user to the dashboard
def forbidden_error(error):
    flash('You do not have permission to access this resource.', 'danger')
    return redirect(url_for('entries.dashboard'))

@bp.errorhandler(404)
# Error handler for 404 Not Found errors
# Flashes an error message and redirects the user to the dashboard
def not_found_error(error):
    flash('The requested resource was not found.', 'danger')
    return redirect(url_for('entries.dashboard'))
