import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)

ENV = 'pro'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xuijhtqmoyikzo:15b8cb464e2fad66693e89dcb4d8e8b8b93b789281259de9a822399a536a42a4@ec2-54-159-113-254.compute-1.amazonaws.com:5432/dt563jahevl50'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class userInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(200))
    created_on = db.Column(db.DateTime)
    profile_url = db.Column(db.String(250))
    followers = db.Column(db.Integer)

    def __init__(self, user_name, password, email, created_on, profile_url, followers):
        self.user_name = user_name
        self.password = password
        self.email = email
        self.created_on = created_on
        self.profile_url = profile_url
        self.followers = followers

app.config['JWT_SECRET_KEY'] = 'qwertyuioplmnbvcxzasdfghjk'
jwt = JWTManager(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'message': 'Hello World!', 'User': 'Test User'})


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username == 'test' or password == 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route('/protected', methods=['GET', 'POST'])
@jwt_required
def protected():
    
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        return jsonify({"user": request.json['user'], "logged_in_as": current_user, "data": request.json['data']})
    
    
    return jsonify(logged_in_as=current_user), 200


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        return 'Hello, There!'
    else:
        return 'Hello'


if __name__ == '__main__':
    app.debug = True
    app.run()