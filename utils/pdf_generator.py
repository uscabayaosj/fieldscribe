from flask import render_template
from weasyprint import HTML
import tempfile

def generate_pdf(entry):
    html_content = render_template('pdf_template.html', entry=entry)
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        HTML(string=html_content).write_pdf(pdf_file.name)
        pdf_content = pdf_file.read()
    
    return pdf_content
