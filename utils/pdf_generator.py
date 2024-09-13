from flask import render_template
from weasyprint import HTML
import tempfile
from datetime import datetime
from pytz import timezone

def generate_pdf(entry, user_timezone):
    # Convert UTC timestamp to user's local time
    utc_time = entry.timestamp.replace(tzinfo=timezone('UTC'))
    local_time = utc_time.astimezone(timezone(user_timezone))
    
    # Format the timestamp
    entry.formatted_timestamp = local_time.strftime('%B %d, %Y at %I:%M %p %Z')
    
    html_content = render_template('pdf_template.html', entry=entry)
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        HTML(string=html_content).write_pdf(pdf_file.name)
        pdf_content = pdf_file.read()
    
    return pdf_content
