from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "API information coming soon"

if __name__ == '__main__':
    app.run(debug=True, port=5010, host='0.0.0.0')
