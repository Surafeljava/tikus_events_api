import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import logout_user
from datetime import timedelta
import os

from werkzeug.utils import secure_filename

#from app import  userInfo
#from app import db
from flask import request, render_template,jsonify
from datetime import datetime as dt
import hashlib
#from app import userInfo
from flask import current_app as app

# Sending mail
from flask_mail import Mail,Message
import socket

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
app.permanent_session_lifetime = timedelta(minutes=1)

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
    reset_link=db.Column(db.String(255))

    def __init__(self, user_name, password, email, created_on, profile_url, followers,reset_link):
        self.user_name = user_name
        self.password = password
        self.email = email
        self.created_on = created_on
        self.profile_url = profile_url
        self.followers = followers
        self.reset_link=reset_link
    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'email': self.email,
            'password':self.password,
            'created_on':self.created_on,
            'profile_url':self.profile_url,
            'followers':self.followers,
            'reset_link':self.reset_link
        }

app.config['SECRET_KEY'] = 'qwertyuioplmnbvcxzasdfghjk'
jwt = JWTManager(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['MAIL_SERVER']='mail.tikusEvent.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']='tikusevents@gmail.com'
app.config['MAIL_PASSWORD']='TikusEvents@5'
# import socket

#app.config.from_pyfile('config.cfg')
mail=Mail(app)
# @app.route('/sendMail')
def sendMailDemo(email,hashCode):
    socket.getaddrinfo('127.0.0.1', 5000)
    msg=Message("Hello,Check this out",recipients=[email],sender='tikusevents@gmail.com')
    msg.body = "Greeting,\nWe've received a request to reset your password. If you want to reset your password, click the link below and enter your new password\n " + hashCode       
    mail.send(msg)
    

    # return jsonify({"message":"Mail Sent Succesfully"})


@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'message': 'Hello World!', 'User': 'Test User', 'requesData': request.args.get('abc')})

@app.route('/user/updateprofile',methods=["POST","GET"])
@jwt_required
def updateUserProfile():
    current_user = get_jwt_identity()
    if current_user:
        user =db.session.query(userInfo).filter_by(user_name=current_user).first()
    
        file=request.files['file']
        file.save(os.path.join('uploads', file.filename))
        user.profile_url=file.filename
        db.session.commit()
        return jsonify({"filename":file.filename})

@app.route('/changePassword',methods=["POST","GET"])
@jwt_required
def changePassword():
    if request.method=="POST":
        userSess=get_jwt_identity()
        """User Password"""
        user=request.get_json()
        pass1=user["old_password"]
        newPass=user["password"]
        
        if pass1 and newPass:
            user =db.session.query(userInfo).filter_by(user_name=userSess).first()
            hashed= hashlib.sha256(pass1.encode())
            password_check= hashed.hexdigest()

            hashedNew=hashlib.sha256(newPass.encode())
            newPassCheck=hashedNew.hexdigest()
            if (not user):
                return jsonify({"message":"User doesnot exist"})
            elif(user.password!=password_check):
                return jsonify({"message":"incorrect old password"})
            else:
                user.password=newPassCheck
                db.session.commit()
                return jsonify({"message":"Password Changed Succesfully"}),200
            return jsonify({"message":"nothing"})
        else:
            return jsonify({"message":"Input must not be empty"})    

import random
@app.route('/forgotPassword',methods=["POST","GET"])
def forgotPassword():
    current_user=get_jwt_identity()
    if current_user:
        return jsonify({"message":"user already logged in"})
    if request.method=="POST":
        user=request.get_json()
        uEmail=user["email"]
        if not uEmail:
            return jsonify({"Error Message":"No Email Address"})
        else:
            userEmail=db.session.query(userInfo).filter_by(email=uEmail).first()
            if not userEmail:
                return jsonify({"Error":"User doesnot exist"})
        def get_random_string(length=24,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
            return ''.join(random.choice(allowed_chars) for i in range(length))
            # return jsonify({"message":name})
        hashCode = get_random_string()  
        sendMailDemo(uEmail,hashCode)
        userEmail.reset_link=hashCode
        db.session.commit()          
        return jsonify({"message":"Reset Link sent to your email address"})

@app.route("/resetPassword",methods=["POST","GET"])
def resetPassword():
    user=request.get_json()
    reset_link=user["reset_link"]
    password=user["password"]
    if not reset_link or not password:
        return jsonify({"msg":"Input can not be empty"})
    exist=db.session.query(userInfo).filter_by(reset_link=reset_link).first()
    if not exist:
        return jsonify({"msg":"User Doesnot Exist"})
    hashed= hashlib.sha256(password.encode())
    hashedPassword= hashed.hexdigest()
    exist.password=hashedPassword
    exist.reset_link=""
    db.session.commit()
    return jsonify({"message":"reset Succesfully,now u can login into ur account"})    

@app.route('/user/viewAllUsers',methods=['GET'])
@jwt_required
def getAllUsers():
    current_user=get_jwt_identity()
    user=db.session.query(userInfo).all()
    # result=users_schema.dumps(user)
    if user:
        # return jsonify(result=result)
        return jsonify(user=[i.serialize for i in user])


    else:
        return jsonify({"message":"no user"},)


@app.route('/display', methods=['GET'])
def displayImage():
    user =db.session.query(userInfo).filter_by(user_name="leali").first()
    filename='uploads/' + user.profile_url
    return jsonify({"filename":filename})

@app.route('/logout', methods=['GET'])
@jwt_required
def logout():
    current_user=get_jwt_identity()

    session.pop('user', None)

    #user =db.session.query(userInfo).filter_by(email=email).first()
    return jsonify({'message':"User Logged Out"}),200

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    user = request.get_json()
    username=user['user_name']
    password=user['password']
    email=user['email']
    #remember = True if user['remember'] else False
    #username = request.json.get('user_name', None)
    #password = request.json.get('password', None)
    if not username :
        return jsonify({"msg": "Missing username parameter"}), 400
    if not email :
        return jsonify({"msg": "Missing email parameter"}), 400    
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    if username == 'test' or password == 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    
    user =db.session.query(userInfo).filter_by(email=email).first()
    hashed= hashlib.sha256(password.encode())
    password_check= hashed.hexdigest()
            
    if (not user ):
        return jsonify({"message":"Incorrect Email or Password"})
    elif( user.password!=password_check):
        return jsonify({"msg": "Incorrect Password or Email"})
    else:    
        access_token = create_access_token(identity=username)
        #set_session_timeout()
        session.permanent = True
        session['user']=username
        
        return jsonify({"msg":"Logged in success","token":access_token}),200
    # Identity can be any data that is json serializable
    # access_token = create_access_token(identity=username)
    
    # return jsonify(access_token=access_token), 200

@app.route('/protected', methods=['GET', 'POST'])
@jwt_required
def protected():
    
    current_user = get_jwt_identity()
    
    if request.method == 'POST':
        return jsonify({"user": request.json['user_name'], "logged_in_as": current_user, "email": request.json['email']})
    
    
    return jsonify(logged_in_as=current_user), 200


@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        return 'Hello, There!'
    else:
        return 'Hello'



@app.route("/register", methods=["POST","GET"])
def register():
    user = request.get_json(force=True)
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

    new_user = userInfo(user_name=username1,password=password,email=email1,created_on=created_on1,profile_url=profile_url1,followers=10,reset_link="")
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