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
from forms import EntryForm  # Assuming a new form class has been created in a 'forms' module.
from functools import wraps

bp = Blueprint('entries', __name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.StreamHandler()])

def owner_required(f):
    @wraps(f)
    def decorated_function(entry_id, *args, **kwargs):
        entry = Entry.query.get_or_404(entry_id)
        if entry.user_id != current_user.id:
            abort(403)
        return f(entry, *args, **kwargs)
    return decorated_function

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    try:
        # Get the current page number from the request arguments, default to 1
        page = request.args.get('page', 1, type=int)
        # Get the number of entries to display per page, default to 5
        per_page = request.args.get('per_page', 5, type=int)
        # Query entries for the current user, ordered by date in descending order, with pagination
        entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).paginate(page=page, per_page=per_page)
        return render_template('dashboard.html', entries=entries)
    except Exception as e:
        # Log the error with traceback information and notify the user
        logging.error(json.dumps({"error": "Error loading dashboard", "exception": str(e)}), exc_info=True)
        flash("An error occurred while loading your dashboard. Please try again.", "error")
        return redirect(url_for('index'))

@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    if form.validate_on_submit():
        try:
            # Extract form data
            title = form.title.data
            content = form.content.data
            location = form.location.data
            tags = [tag.strip() for tag in form.tags.data.split(',')]
            
            # Create a new Entry object
            entry = Entry(title=title, content=content, location=location, user_id=current_user.id, date=datetime.utcnow())
            db.session.add(entry)

            # Fetch all tags at once to reduce database queries
            existing_tags = Tag.query.filter(Tag.name.in_(tags)).all()
            existing_tag_names = {tag.name: tag for tag in existing_tags}

            # Add tags if applicable
            for tag_name in tags:
                if tag_name in existing_tag_names:
                    tag = existing_tag_names[tag_name]
                else:
                    # Create a new Tag if it doesn't exist
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                # Append the tag to the entry if it is not already associated
                if tag not in entry.tags:
                    entry.tags.append(tag)

            # Commit the transaction
            db.session.commit()

            flash("New entry created successfully!", "success")
            return redirect(url_for('entries.dashboard'))
        except Exception as e:
            # Rollback the transaction in case of an error
            db.session.rollback()
            logging.error(json.dumps({"error": "Error creating new entry", "exception": str(e)}), exc_info=True)
            flash("An error occurred while creating the entry. Please try again.", "error")
    elif request.method == 'POST':
        # If form validation fails, notify the user
        flash("Please correct the errors in the form.", "error")

    return render_template('new_entry.html', form=form)

@bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_entry(entry, entry_id):
    form = EntryForm(obj=entry)
    if form.validate_on_submit():
        try:
            # Update the entry with form data
            entry.title = form.title.data
            entry.content = form.content.data
            entry.location = form.location.data
            tags = [tag.strip() for tag in form.tags.data.split(',')]
            
            # Compare existing tags with new ones and update accordingly
            existing_tags = {tag.name for tag in entry.tags}
            new_tags = set(tags)

            # Fetch all new tags at once to reduce database queries
            all_tags = Tag.query.filter(Tag.name.in_(new_tags)).all()
            tag_map = {tag.name: tag for tag in all_tags}

            # Add new tags
            for tag_name in new_tags - existing_tags:
                if tag_name in tag_map:
                    tag = tag_map[tag_name]
                else:
                    # Create a new Tag if it doesn't exist
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                # Append the tag to the entry if it is not already associated
                if tag not in entry.tags:
                    entry.tags.append(tag)

            # Remove old tags
            for tag_name in existing_tags - new_tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    # Remove the tag from the entry
                    entry.tags.remove(tag)

            # Commit the transaction
            db.session.commit()

            flash("Entry updated successfully!", "success")
            return redirect(url_for('entries.dashboard'))
        except Exception as e:
            # Rollback the transaction in case of an error
            db.session.rollback()
            logging.error(json.dumps({"error": "Error updating entry", "exception": str(e)}), exc_info=True)
            flash("An error occurred while updating the entry. Please try again.", "error")

    return render_template('edit_entry.html', form=form)

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_entry(entry, entry_id):
    try:
        # Delete the entry from the database
        db.session.delete(entry)
        # Commit the transaction
        db.session.commit()
        flash("Entry deleted successfully!", "success")
    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        logging.error(json.dumps({"error": "Error deleting entry", "exception": str(e)}), exc_info=True)
        flash("An error occurred while deleting the entry. Please try again.", "error")

    return redirect(url_for('entries.dashboard'))

# Form class for entry (assuming you have Flask-WTF installed)
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class EntryForm(FlaskForm):
    # Title field with data required and maximum length validation
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    # Content field with data required validation
    content = TextAreaField('Content', validators=[DataRequired()])
    # Location field with optional maximum length validation
    location = StringField('Location', validators=[Length(max=100)])
    # Tags field for comma-separated tags
    tags = StringField('Tags')
    # Submit button
    submit = SubmitField('Submit')
