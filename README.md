# FieldScribe Pro

FieldScribe Pro is a Flask-based web application designed for journal entry management. It provides user authentication, admin functionality, and a dashboard for managing journal entries.

## Features

- User registration and authentication
- Admin user management
- Journal entry creation, reading, updating, and deletion
- Dashboard for viewing and managing entries
- Responsive design using Tailwind CSS

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.7+
- PostgreSQL database
- pip (Python package manager)

## Installation

1. Clone the repository:
  - `git clone https://github.com/yourusername/fieldscribe-pro.git`
  - `cd fieldscribe-pro`


2. Set up a virtual environment:
  -  `python -m venv venv`
  -  `source venv/bin/activate`
    
  On Windows use
  - `venv\Scripts\activate`

3. Install the required packages:
  - `pip install -r requirements.txt`
4. Set up environment variables:
Create a `.env` file in the root directory and add the following:
  - `SECRET_KEY=your_secret_key`
  - `DATABASE_URL=postgresql://username:password@localhost/database_name`

Replace `your_secret_key`, `username`, `password`, and `database_name` with your actual values.

5. Initialize the database:
  - `flask db init`
  - `flask db migrate -m "Initial migration"`
  - `flask db upgrade`


## Usage

To run the application:

1. Ensure you're in the project directory and your virtual environment is activated.

2. Set the Flask application:
   - `export FLASK_APP=main.py`
   - # On Windows use
   - `set FLASK_APP=main.py`

4. Run the application:
   - `flask run`

6. Open a web browser and navigate to `http://localhost:5000`

## Development

To contribute to FieldScribe Pro, follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b <branch_name>`
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/articles/creating-a-pull-request/).

## Contact

If you want to contact the maintainer, you can reach out at [your-email@example.com](mailto:your-email@example.com).

## License

This project uses the following license: [MIT License](https://opensource.org/licenses/MIT).
