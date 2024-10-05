import unittest
from flask import url_for
from flask_app import create_app
from flask_app.extensions import db
from flask_app.models import User, Entry
from io import BytesIO

class TestEntriesRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_export_entry(self):
        # Create a test user and entry
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()  # Commit to get the user.id

        entry = Entry(title='Test Entry', content='Test Content', user_id=user.id)
        db.session.add(entry)
        db.session.commit()

        # Log in the user
        with self.client:
            self.client.post('/login', data=dict(
                username='testuser',
                password='testpassword'
            ), follow_redirects=True)

            # Test exporting the entry
            response = self.client.get(f'/entry/{entry.id}/export')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/pdf')
            self.assertTrue(response.headers['Content-Disposition'].startswith('attachment; filename=entry_'))
            self.assertGreater(len(response.data), 0)

if __name__ == '__main__':
    unittest.main()
