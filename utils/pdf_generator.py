from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import pytz
from flask import url_for

def generate_pdf(entry, timezone):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))  # 4 is for justified text
    
    story = []
    
    # Title
    story.append(Paragraph(entry.title, styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Date and Location
    tz = pytz.timezone(timezone)
    local_date = entry.date.replace(tzinfo=pytz.UTC).astimezone(tz)
    date_str = local_date.strftime("%Y-%m-%d %H:%M:%S %Z")
    story.append(Paragraph(f"Date: {date_str}", styles['Normal']))
    if entry.location:
        story.append(Paragraph(f"Location: {entry.location}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Content
    story.append(Paragraph(entry.content, styles['Justify']))
    story.append(Spacer(1, 12))
    
    # Tags
    if entry.tags:
        tags_str = ", ".join([tag.name for tag in entry.tags])
        story.append(Paragraph(f"Tags: {tags_str}", styles['Italic']))
    
    # Associated Media
    if entry.media:
        story.append(Spacer(1, 12))
        story.append(Paragraph("Associated Media:", styles['Heading3']))
        for media in entry.media:
            if media.media_type == 'image':
                img_path = url_for('static', filename=f'uploads/{media.filename}', _external=True)
                img = Image(img_path, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(f"Media: {media.filename} ({media.media_type})", styles['Normal']))
    
    doc.build(story)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
