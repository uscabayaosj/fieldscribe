from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from flask_app.models import Entry, Tag
from flask_app.extensions import db
from utils.thematic_analysis import perform_thematic_analysis
from utils.pdf_generator import generate_pdf
import json
import logging
import tempfile

bp = Blueprint('entries', __name__)

# ... (rest of the existing code)

@bp.route('/export_analysis_pdf')
@login_required
def export_analysis_pdf():
    try:
        entries = Entry.query.filter_by(user_id=current_user.id).all()
        serialized_entries = []
        for entry in entries:
            serialized_entry = {
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'date': entry.date.isoformat(),
                'location': entry.location,
                'tags': [tag.name for tag in entry.tags]
            }
            serialized_entries.append(serialized_entry)
        
        analysis_result = perform_thematic_analysis(serialized_entries)
        
        pdf_content = generate_pdf(analysis_result, 'analysis')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        return send_file(
            temp_file_path,
            as_attachment=True,
            download_name="thematic_analysis.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        logging.error(json.dumps({"error": "Error exporting analysis PDF", "exception": str(e)}), exc_info=True)
        flash("An error occurred while exporting the analysis. Please try again.", "error")
        return redirect(url_for('entries.analyze_entries'))