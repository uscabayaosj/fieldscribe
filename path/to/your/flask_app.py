from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Ensure this template exists in the 'templates' directory

# ... other route definitions ...

if __name__ == '__main__':
    app.run(debug=True)  # Run in debug mode for detailed error messages