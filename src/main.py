from router import routes
from flask import Flask
app = Flask(__name__)
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)