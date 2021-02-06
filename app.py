import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


#from app import  userInfo
#from app import db
from flask import request, render_template,jsonify
from datetime import datetime as dt
import hashlib
#from app import userInfo
from flask import current_app as app

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)

ENV = 'pro'

if ENV == 'dev':
    app.debug = True
    #app.config['SQLALCHEMY_DATABASE_URI'] = ''
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:berrybab0764@localhost:5432/TikusEvent'
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:berrybab0764@localhost:5432/TikusEvent'

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

#from routes import register
@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'message': 'Hello World!', 'User': 'Test User', 'requesData': request.args.get('abc')})


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

@app.route("/register", methods=["POST","GET"])
def register():
    user = request.get_json()
    #print (content)
    username1=user["user_name"]
    email1=user["email"]
    #user_id=user["user_id"]
    password1=user["password"]
    created_on1=dt.now()
    profile_url1="t.me/berrybab6"
    #followers=0
    
    if email1 == "":
        message = "Please fill in your email address"
        return jsonify({"message":message})
        

    if password1 == "":
        message = "Please fill in your password"
        return jsonify({"message":message})
    if email1 and password1:
        is_exist=userInfo.query.filter(
            userInfo.user_name == username1 or userInfo.email == email1
        ).first()
        if is_exist:
            return jsonify({"message":"User already Exists"})

    #Hash Password
    hashed = hashlib.sha256(password1.encode())
    password = hashed.hexdigest()
    #db_conn = psycopg2.connect(host=db_host, port=db_port, dbname=dbname, user=db_user, password=pw)
    #db_cursor = db_conn.cursor()

    new_user = userInfo(user_name=username1,password=password,email=email1,created_on=created_on1,profile_url=profile_url1,followers=10)
    db.session.add(new_user)
    #db_conn.session.commit()


    #db_cursor.execute(new_user)
    try:
        db.session.commit()
    except psycopg2.Error as e:
        message = "Database error: " + e + "/n SQL: " + new_user
        return jsonify({"message":message}),401 #render_template("register.html", message = t_message)

    message = "Your user account has been added."
    return jsonify({"message":message,"username":username1})


if __name__ == '__main__':
    app.debug = True
    app.run()
#from routes import register