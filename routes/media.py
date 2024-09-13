from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Entry, Media
from __init__ import db
import os

bp = Blueprint('media', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload/<int:entry_id>', methods=['POST'])
@login_required
def upload_file(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        media_type = filename.rsplit('.', 1)[1].lower()
        media = Media(filename=filename, media_type=media_type, entry_id=entry.id)
        db.session.add(media)
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    
    return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/media/<int:media_id>/delete', methods=['POST'])
@login_required
def delete_media(media_id):
    media = Media.query.get_or_404(media_id)
    if media.entry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], media.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(media)
    db.session.commit()
    
    return jsonify({'message': 'Media deleted successfully'}), 200
