from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

def generate_pdf(content, content_type='entry'):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))
    
    story = []
    
    if content_type == 'entry':
        # Existing entry PDF generation code
        pass
    elif content_type == 'analysis':
        story.append(Paragraph("Thematic Analysis of Journal Entries", styles['Title']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Main Themes", styles['Heading2']))
        themes_list = ListFlowable(
            [ListItem(Paragraph(theme, styles['Normal'])) for theme in content['main_themes']],
            bulletType='bullet',
            start='',
            leftIndent=20
        )
        story.append(themes_list)
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Emotions", styles['Heading2']))
        emotions_list = ListFlowable(
            [ListItem(Paragraph(emotion, styles['Normal'])) for emotion in content['emotions']],
            bulletType='bullet',
            start='',
            leftIndent=20
        )
        story.append(emotions_list)
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Patterns", styles['Heading2']))
        patterns_list = ListFlowable(
            [ListItem(Paragraph(pattern, styles['Normal'])) for pattern in content['patterns']],
            bulletType='bullet',
            start='',
            leftIndent=20
        )
        story.append(patterns_list)
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Summary", styles['Heading2']))
        story.append(Paragraph(content['summary'], styles['Normal']))
    
    doc.build(story)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
