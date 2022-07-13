from flask import Flask, jsonify
from flask_restx import Api
from setup_db import db
from views import advert_ns, user_ns, bcrypt, HttpError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://user:password@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

api = Api(app)

bcrypt.init_app(app)

api.add_namespace(advert_ns)
api.add_namespace(user_ns)

with app.app_context():
    db.create_all()

@app.errorhandler(HttpError)
def http_error_handler(error):
    return jsonify({'error': error.error_message}), error.status_code

if __name__ == '__main__':
    app.run(debug=True)
