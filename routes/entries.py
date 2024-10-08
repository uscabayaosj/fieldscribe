from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, abort, current_app, send_file
from flask_login import login_required, current_user
from flask_app.models import Entry, Tag, Media, AnalysisResult
from flask_app.extensions import db
from utils.pdf_generator import generate_pdf
from utils.thematic_analysis import perform_thematic_analysis
import json
import logging
from datetime import datetime
import pytz
from werkzeug.utils import secure_filename
import os
from forms import EntryForm
from functools import wraps
import tempfile
import secrets

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
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).paginate(page=page, per_page=per_page)
        return render_template('dashboard.html', entries=entries)
    except Exception as e:
        logging.error(json.dumps({"error": "Error loading dashboard", "exception": str(e)}), exc_info=True)
        flash("An error occurred while loading your dashboard. Please try again.", "error")
        return redirect(url_for('index'))

@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    if form.validate_on_submit():
        try:
            project = form.project.data
            title = form.title.data
            location = form.location.data
            context = form.context.data
            detailed_observation = form.detailed_observation.data
            reflection = form.reflection.data
            tags = [tag.strip() for tag in form.tags.data.split(',')]
            
            entry = Entry(project=project, title=title, location=location, context=context,
                          detailed_observation=detailed_observation, reflection=reflection,
                          user_id=current_user.id, date=datetime.utcnow())
            db.session.add(entry)

            existing_tags = Tag.query.filter(Tag.name.in_(tags)).all()
            existing_tag_names = {tag.name: tag for tag in existing_tags}

            for tag_name in tags:
                if tag_name in existing_tag_names:
                    tag = existing_tag_names[tag_name]
                else:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                if tag not in entry.tags:
                    entry.tags.append(tag)

            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename != '':
                    filename = secure_filename(photo.filename)
                    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    photo.save(photo_path)
                    media = Media(filename=filename, entry_id=entry.id, media_type='image')
                    db.session.add(media)

            db.session.commit()

            flash("New entry created successfully!", "success")
            return redirect(url_for('entries.dashboard'))
        except Exception as e:
            db.session.rollback()
            logging.error(json.dumps({"error": "Error creating new entry", "exception": str(e)}), exc_info=True)
            flash("An error occurred while creating the entry. Please try again.", "error")
    elif request.method == 'POST':
        flash("Please correct the errors in the form.", "error")

    return render_template('new_entry.html', form=form)

@bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_entry(entry):
    form = EntryForm(obj=entry)
    if form.validate_on_submit():
        try:
            entry.project = form.project.data
            entry.title = form.title.data
            entry.location = form.location.data
            entry.context = form.context.data
            entry.detailed_observation = form.detailed_observation.data
            entry.reflection = form.reflection.data
            tags = [tag.strip() for tag in form.tags.data.split(',')]
            
            existing_tags = {tag.name for tag in entry.tags}
            new_tags = set(tags)

            all_tags = Tag.query.filter(Tag.name.in_(new_tags)).all()
            tag_map = {tag.name: tag for tag in all_tags}

            for tag_name in new_tags - existing_tags:
                if tag_name in tag_map:
                    tag = tag_map[tag_name]
                else:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                if tag not in entry.tags:
                    entry.tags.append(tag)

            for tag_name in existing_tags - new_tags:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    entry.tags.remove(tag)

            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename != '':
                    filename = secure_filename(photo.filename)
                    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    photo.save(photo_path)
                    
                    old_media = Media.query.filter_by(entry_id=entry.id).first()
                    if old_media:
                        db.session.delete(old_media)
                    
                    media = Media(filename=filename, entry_id=entry.id, media_type='image')
                    db.session.add(media)

            db.session.commit()

            flash("Entry updated successfully!", "success")
            return redirect(url_for('entries.dashboard'))
        except Exception as e:
            db.session.rollback()
            logging.error(json.dumps({"error": "Error updating entry", "exception": str(e)}), exc_info=True)
            flash("An error occurred while updating the entry. Please try again.", "error")

    return render_template('edit_entry.html', form=form, entry=entry)

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_entry(entry):
    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Entry deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logging.error(json.dumps({"error": "Error deleting entry", "exception": str(e)}), exc_info=True)
        flash("An error occurred while deleting the entry. Please try again.", "error")

    return redirect(url_for('entries.dashboard'))

@bp.route('/entry/<int:entry_id>', methods=['GET'])
@login_required
@owner_required
def view_entry(entry):
    try:
        media = Media.query.filter_by(entry_id=entry.id).first()
        return render_template('entry_detail.html', entry=entry, media=media)
    except Exception as e:
        logging.error(json.dumps({"error": "Error viewing entry", "exception": str(e)}), exc_info=True)
        flash("An error occurred while viewing the entry. Please try again.", "error")
        return redirect(url_for('entries.dashboard'))

@bp.route('/entry/<int:entry_id>/export', methods=['GET'])
@login_required
@owner_required
def export_entry(entry):
    try:
        timezone = request.args.get('timezone', 'UTC')
        pdf_content = generate_pdf(entry, timezone)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name=f"entry_{entry.id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        logging.error(json.dumps({"error": "Error exporting entry", "exception": str(e)}), exc_info=True)
        flash("An error occurred while exporting the entry. Please try again.", "error")
        return redirect(url_for('entries.view_entry', entry_id=entry.id))

@bp.route('/entry/<int:entry_id>/share', methods=['POST'])
@login_required
@owner_required
def share_entry(entry):
    try:
        share_token = secrets.token_urlsafe(16)
        
        entry.share_token = share_token
        db.session.commit()
        
        share_url = url_for('entries.view_shared_entry', share_token=share_token, _external=True)
        
        return jsonify({'share_url': share_url}), 200
    except Exception as e:
        logging.error(json.dumps({"error": "Error sharing entry", "exception": str(e)}), exc_info=True)
        return jsonify({'error': 'An error occurred while sharing the entry'}), 500

@bp.route('/shared/<string:share_token>')
def view_shared_entry(share_token):
    entry = Entry.query.filter_by(share_token=share_token).first_or_404()
    return render_template('shared_entry.html', entry=entry)

@bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze_entries():
    if request.method == 'POST':
        try:
            entries = Entry.query.filter_by(user_id=current_user.id).all()
            serialized_entries = []
            for entry in entries:
                serialized_entry = {
                    'id': entry.id,
                    'title': entry.title,
                    'project': entry.project,
                    'location': entry.location,
                    'context': entry.context,
                    'detailed_observation': entry.detailed_observation,
                    'reflection': entry.reflection,
                    'date': entry.date.isoformat(),
                    'tags': [tag.name for tag in entry.tags]
                }
                serialized_entries.append(serialized_entry)
            
            analysis_result = perform_thematic_analysis(serialized_entries)
            
            new_analysis = AnalysisResult(user_id=current_user.id, content=analysis_result)
            db.session.add(new_analysis)
            db.session.commit()
            
            flash("Analysis completed and saved successfully!", "success")
            return render_template('analysis_result.html', analysis_result=analysis_result)
        except Exception as e:
            logging.error(f"Error analyzing entries: {str(e)}", exc_info=True)
            flash("An error occurred while analyzing the entries. Please try again.", "error")
            return redirect(url_for('entries.dashboard'))
    else:
        latest_analysis = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(AnalysisResult.date.desc()).first()
        return render_template('analyze.html', latest_analysis=latest_analysis)

@bp.route('/analysis_history')
@login_required
def analysis_history():
    analysis_results = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(AnalysisResult.date.desc()).all()
    return render_template('analysis_history.html', analysis_results=analysis_results)

@bp.route('/delete_analysis/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    if analysis.user_id != current_user.id:
        abort(403)  # Forbidden
    
    db.session.delete(analysis)
    db.session.commit()
    flash('Analysis result deleted successfully', 'success')
    return redirect(url_for('entries.analysis_history'))