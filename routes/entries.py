from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, abort
from flask_login import login_required, current_user
from models import Entry, Tag, Media
from __init__ import db
from utils.pdf_generator import generate_pdf
import json

bp = Blueprint('entries', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    entries = Entry.query.filter_by(user_id=current_user.id).order_by(Entry.date.desc()).all()
    return render_template('dashboard.html', entries=entries)

@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        location = request.form['location']
        tags = request.form.getlist('tags')
        
        entry = Entry(title=title, content=content, location=location, user_id=current_user.id)
        
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            entry.tags.append(tag)
        
        db.session.add(entry)
        db.session.commit()
        
        flash('New entry created successfully!', 'success')
        return redirect(url_for('entries.dashboard'))
    
    return render_template('entry_form.html')

@bp.route('/entry/<int:id>')
@login_required
def view_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    return render_template('entry_detail.html', entry=entry)

@bp.route('/entry/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        entry.title = request.form['title']
        entry.content = request.form['content']
        entry.location = request.form['location']
        
        entry.tags.clear()
        tags = request.form.getlist('tags')
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
            entry.tags.append(tag)
        
        db.session.commit()
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('entries.view_entry', id=entry.id))
    
    return render_template('entry_form.html', entry=entry)

@bp.route('/entry/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('entries.dashboard'))

@bp.route('/entry/<int:id>/export')
@login_required
def export_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    pdf_content = generate_pdf(entry)
    return pdf_content, 200, {'Content-Type': 'application/pdf'}

@bp.route('/entry/<int:id>/share', methods=['POST'])
@login_required
def share_entry(id):
    entry = Entry.query.get_or_404(id)
    if entry.user_id != current_user.id:
        abort(403)
    
    share_url = url_for('entries.view_entry', id=entry.id, _external=True)
    return jsonify({'share_url': share_url})

@bp.errorhandler(403)
def forbidden_error(error):
    flash('You do not have permission to access this resource.', 'error')
    return redirect(url_for('entries.dashboard'))

@bp.errorhandler(404)
def not_found_error(error):
    flash('The requested resource was not found.', 'error')
    return redirect(url_for('entries.dashboard'))
