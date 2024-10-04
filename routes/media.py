import logging
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Entry, Media
from __init__ import db
import uuid
from functools import wraps
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
import magic
from sqlalchemy.orm import lazyload

# Define a Blueprint for media-related routes
bp = Blueprint('media', __name__)

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}
# Maximum file size allowed (in MB)
MAX_FILE_SIZE_MB = 10
# Minimum file size allowed (in bytes)
MIN_FILE_SIZE_BYTES = 1024  # 1 KB

# Helper function to check if the file extension is allowed and validate MIME type
def allowed_file(file):
    # Check if the filename contains a '.' and if the extension is in the allowed list
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return False
    # Check the MIME type using python-magic
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(file.read(1024))
    except Exception as e:
        current_app.logger.error(f"Error determining MIME type: {e}")
        return False
    finally:
        file.seek(0)  # Reset file pointer after reading
    allowed_mime_types = {
        'image/png', 'image/jpeg', 'image/gif',
        'audio/mpeg', 'video/mp4'
    }
    return mime_type in allowed_mime_types

# Decorator for checking entry ownership
def entry_owner_required(f):
    @wraps(f)
    def decorated_function(entry_id, *args, **kwargs):
        entry = Entry.query.options(lazyload(Entry.media)).get_or_404(entry_id)
        if entry.user_id != current_user.id:
            current_app.logger.error(f"Unauthorized attempt by user {current_user.id}")
            return jsonify({'error': 'Unauthorized'}), 403
        return f(entry, *args, **kwargs)
    return decorated_function

# Route to render file upload UI (HTML for drag-and-drop or input form)
@bp.route('/upload_form')
@login_required
# Render an HTML form for file uploads
# The form could include drag-and-drop functionality or a simple file input
# This helps to provide a user-friendly interface for uploading files
def upload_form():
    return render_template('upload_form.html')

# Endpoint to handle media file uploads for a specific entry
@bp.route('/upload/<int:entry_id>', methods=['POST'])
@login_required
@entry_owner_required
def upload_file(entry):
    # Check if the request contains a file and if a file was selected
    file = request.files.get('file')
    if file is None or file.filename == '':
        current_app.logger.error("No file part or no selected file")
        return jsonify({'error': 'No file part or no selected file'}), 400

    # Check if the file size is too small
    file.seek(0, 2)  # Move to the end of the file to get its size
    file_size = file.tell()
    file.seek(0)  # Reset file pointer after getting the size
    if file_size < MIN_FILE_SIZE_BYTES:
        current_app.logger.error(f"File size is too small: {file_size} bytes")
        return jsonify({'error': f'File too small. Minimum allowed size is {MIN_FILE_SIZE_BYTES} bytes'}), 400

    # If the file is allowed, save it
    if allowed_file(file):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        # Define the path where the file will be saved using pathlib
        save_path = Path(current_app.config['UPLOAD_FOLDER']) / unique_filename
        # Ensure the target directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Save the file to the specified path
            file.save(save_path)
            # Create a new Media record in the database
            new_media = Media(entry_id=entry.id, filename=unique_filename)
            db.session.add(new_media)
            db.session.commit()
            # Return a success response with the filename
            return jsonify({'message': 'File successfully uploaded', 'filename': unique_filename}), 201
        except SQLAlchemyError as db_error:
            db.session.rollback()
            current_app.logger.error(f"Database error: {db_error}")
            return jsonify({'error': 'Failed to save file to database'}), 500
        except Exception as e:
            # Log any errors that occur while saving the file
            current_app.logger.error(f"Error saving file: {e}")
            return jsonify({'error': 'Failed to save file'}), 500
    else:
        # Log an error if the file type is unsupported
        current_app.logger.error("Unsupported file type or MIME type")
        return jsonify({'error': 'Unsupported file type or MIME type'}), 400

# Before request hook to limit the file size of incoming requests
@bp.before_request
def limit_file_size():
    # Check the content length of the incoming request
    request_length = request.content_length
    # If the request length exceeds the maximum allowed size, return an error
    if request_length is not None and request_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        current_app.logger.error(f"File size exceeds limit of {MAX_FILE_SIZE_MB} MB: {request_length}")
        return jsonify({'error': f'File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB'}), 413
