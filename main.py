from flask import Flask, render_template
from __init__ import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
