from flask_app import create_app
from flask_app.extensions import db
from flask_app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created successfully")

    # Verify the User table exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if 'user' in inspector.get_table_names():
        print("User table exists")
    else:
        print("User table does not exist")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)