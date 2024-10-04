from flask import Flask, render_template
from __init__ import create_app  # Assuming your package is named 'journal'

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
