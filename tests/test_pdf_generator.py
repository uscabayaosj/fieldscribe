import unittest
from utils.pdf_generator import generate_pdf
from flask_app.models import Entry
from datetime import datetime

class TestPDFGenerator(unittest.TestCase):
    def test_generate_pdf(self):
        # Create a mock entry
        entry = Entry(
            id=1,
            title="Test Entry",
            content="This is a test entry content.",
            date=datetime.utcnow(),
            location="Test Location"
        )
        
        # Generate PDF
        pdf_content = generate_pdf(entry, "UTC")
        
        # Check if PDF content is generated
        self.assertIsInstance(pdf_content, bytes)
        self.assertTrue(len(pdf_content) > 0)
        
        # Check if PDF starts with the correct header
        self.assertTrue(pdf_content.startswith(b'%PDF'))

if __name__ == '__main__':
    unittest.main()
