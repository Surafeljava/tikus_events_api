import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request,session,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import logout_user
from datetime import timedelta
from sqlalchemy import (
    Column,
    Integer,
    String
)
import os
#from sqlalchemy.dialects.postgresql import UUID
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
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

# register_to_event = db.Table('register_to_event',
#     db.Column('id', UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4().hex),
#     db.Column('user_id', db.Integer, db.ForeignKey('user_info.id')),
#     db.Column('event_id', db.Integer, db.ForeignKey('event_info.event_id')),
#     db.Column('seat_num', db.Integer,unique=True)

# )

class userInfo(db.Model):
    __tablename__ = 'user_info'
    __table_args__ = {'extend_existing':True}
    #__table_args__ = {'schema': 'schema_any'}
    #__abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(200))
    created_on = db.Column(db.DateTime)
    profile_url = db.Column(db.String(250))
    followers = db.Column(db.Integer)
    reset_link=db.Column(db.String(255))
    # event_user = db.relationship("EventInfo",
    #                  secondary=register_to_event,
    #                  backref=db.backref('event_info', lazy='dynamic'))

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

class Registered_To_Event(db.Model):
    __tablename__='register_to_event'
    id = db.Column(db.Integer, primary_key=True)
   # id=db.Column('id', UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'),nullable=False)
    user_info = db.relationship("userInfo", backref=db.backref("user_event", uselist=False))
    event_id = db.Column(db.Integer, db.ForeignKey('event_info.event_id'),nullable=False)
    event_info = db.relationship("EventInfo", backref=db.backref("event_info", uselist=False))
    seat_num=db.Column('seat_num', db.Integer,unique=True)
    event_title = db.Column(db.String(150),nullable=False)
    # event_info = db.relationship("EventInfo", backref=db.backref("event_title", uselist=False))
    """docstring for Registere_To_Event"""
    def __init__(self, user_id,event_id,seat_num,event_title):
        
        self.user_id=user_id
        self.event_id=event_id
        self.seat_num=seat_num
        self.event_title=event_title
    @property
    def serialize(self):
        return {
        'id':self.id,
        'user_id':self.user_id,
        'event_id':self.event_id,
        'seat_num':self.seat_num,
        'event_title':self.event_title
        }


class EventInfo(db.Model):
    __tablename__ = 'event_info'
    event_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'),nullable=False)
    user_info = db.relationship("userInfo", backref=db.backref("user_info", uselist=False))
    title=db.Column(db.String(150))
    description = db.Column(db.String(250))
    event_created_on = db.Column(db.DateTime)
    event_begins_on = db.Column(db.DateTime)
    event_ends_on = db.Column(db.DateTime)
    event_deadline = db.Column(db.DateTime)
    event_picture = db.Column(db.String(250))
    to_be_accepted_users_num = db.Column(db.Integer)
    registered_users_num = db.Column(db.Integer)
    
    

    def __init__(self, user_id,title,description,event_created_on,event_begins_on, event_ends_on,event_deadline,event_picture,to_be_accepted_users_num,registered_users_num):
        #self.event_id = event_id
        self.user_id=user_id
        self.title=title
        self.description = description
        self.event_created_on=event_created_on
        self.event_begins_on=event_begins_on
        self.event_ends_on=event_ends_on
        self.event_deadline=event_deadline
        self.event_picture=event_picture
        self.to_be_accepted_users_num=to_be_accepted_users_num
        self.registered_users_num=registered_users_num
        
    @property
    def serialize(self):
        return {
            'event_id':self.event_id,
            'user_id':self.user_id,
            'title':self.title,
            'description':self.description,
            'event_created_on':self.event_created_on,
            'event_begins_on':self.event_begins_on,
            'event_ends_on':self.event_ends_on,
            'event_deadline':self.event_deadline,
            'event_picture':self.event_picture,
            'to_be_accepted_users_num':self.to_be_accepted_users_num,
            'registered_users_num':self.registered_users_num
            
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


'''
    User Authentication And Authorization

'''
@app.route('/auth/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    user = request.get_json()
    username=user['user_name']
    password=user['password']
    email=user['email']
    if not username and  not password:
        return jsonify({"msg": "Missing username  or password"}), 400
    if not email :
        return jsonify({"msg": "Missing email parameter"}), 400    
    # if not password:
    #     return jsonify({"msg": "Missing password parameter"}), 400

    if username == 'test' or password == 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    
    user =db.session.query(userInfo).filter_by(email=email).first()
    userN=db.session.query(userInfo).filter_by(user_name=username).first()
    if user or usern:
        hashed= hashlib.sha256(password.encode())
        password_check= hashed.hexdigest()
            
        
        if( user.password!=password_check):
            return jsonify({"msg": "Incorrect Password or Email"})
        else:    
            access_token = create_access_token(identity=username)
          
            session.permanent = True
            session['user']=username
            return jsonify({"msg":"Logged in success","token":access_token}),200


@app.route("/auth/register", methods=["POST","GET"])
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


@app.route('/users/changePassword',methods=["PUT"])
@jwt_required
def changePassword():
    if request.method=="PUT":
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
    else:
        return jsonify({"message":"Unable To Change Password"})   

import random
@app.route('/auth/forgotPassword',methods=["POST","GET"])
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

@app.route("/auth/resetPassword",methods=["PUT"])
def resetPassword():
    user=request.get_json()
    reset_link=user["reset_code"]
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

@app.route('/auth/logout', methods=['GET'])
@jwt_required
def logout():
    current_user=get_jwt_identity()

    session.pop('username', None)

    #user =db.session.query(userInfo).filter_by(email=email).first()
    return jsonify({'message':"User Logged Out"}),200

"""
    ######
    User Information
    #######
"""


@app.route('/users/updateprofile',methods=["PUT"])
@jwt_required
def updateUserProfile():
    current_user = get_jwt_identity()
    if current_user:
        user =db.session.query(userInfo).filter_by(user_name=current_user).first()
        if user:
            file=request.files['file']
            file.save(os.path.join('uploads', file.filename))
            user.profile_url=file.filename
            db.session.commit()
            return jsonify({"filename":file.filename})

@app.route('/users/viewAllUsers',methods=['GET'])
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
@jwt_required
def displayImage():
    current_user=get_jwt_identity()
    if current_user:
        user =db.session.query(userInfo).filter_by(user_name=current_user).first()
        filename='uploads/' + user.profile_url
        return jsonify({"filename":filename})

"""
    #######
    Event CRUD operation
    #######

"""

@app.route('/events/addEventPicture',methods=["POST","GET"])
@jwt_required
def addEventPicture():
    current_user = get_jwt_identity()
    if current_user:
        #user =db.session.query(userInfo).filter_by(user_name=current_user).first()

        file=request.files['event_picture']
        try:
            file.save(os.path.join('events', file.filename))
        except:
            return jsonify({"error":"Error while uploading image"}),401
        # user.profile_url=file.filename
        # db.session.commit()
        return jsonify({"filename":file.filename})
    else:
        return jsonify({"mesage":"you are not Signed in"}),403

@app.route('/events/addEvent',methods=["POST"])
@jwt_required
def addevent():
    current_user = get_jwt_identity()
    if not current_user:
        return jsonify({"message":"UnAthenticated User"}),403
    else:
        event = request.get_json(force=True)
        title=event["title"]
        description=event["description"]
        event_picture=event['event_picture']
        
        #user id from UserInfo table
        user =db.session.query(userInfo).filter_by(user_name=current_user).first()
        user_id=user.id
        #user_id=2
        to_be_accepted_users_num=event["sit_limit"]
        #to_be_accepted_users_num=100
        registered_users_num=0
        event_created_on=dt.now()
        event_begins_on=event["event_begins_on"]
        event_ends_on=event["event_ends_on"]
        event_deadline=event["event_deadline"]
        if not title or not to_be_accepted_users_num or not event_picture or not description or not event_begins_on or not event_deadline or not event_ends_on:
            return jsonify({"message":"Fields Can not be Empty"}),401     
        else:
            new_event = EventInfo(user_id=user_id,
                title=title,
                description=description,
                event_created_on=event_created_on,
                event_begins_on=event_begins_on,
                event_ends_on=event_ends_on,
                event_deadline=event_deadline,
                event_picture=event_picture,#file.filename,
                to_be_accepted_users_num=to_be_accepted_users_num,
                registered_users_num=registered_users_num)
            db.session.add(new_event)
            try:
                db.session.commit()
            except psycopg2.Error as e:
                message = "Database error: " + e + "/n SQL: " + new_user
                return jsonify({"message":message}),401 #render_template("register.html", message = t_message)
           
            return jsonify({"message":"event Added Succesfully"})#,event=[new_event.serialize])

@app.route('/events/viewAllEvents',methods=['GET'])
@jwt_required
def getAllEvents():
    current_user=get_jwt_identity()
    if current_user:
        event=db.session.query(EventInfo).all()
        # result=users_schema.dumps(user)
        if event:
            # return jsonify(result=result)
            return jsonify(event=[i.serialize for i in event])
        else:
            return jsonify({"message":"no event"},)

@app.route('/events/getSingleEventById/<int:event_id>',methods=['GET'])
@jwt_required
def getSingleEventById(event_id):
    current_user=get_jwt_identity()
    if current_user:
        event=db.session.query(EventInfo).filter_by(event_id=event_id).first()
        if event:
            return jsonify({"message":"retrieving signle event By ID","event":event.serialize}),200
        else:
            return jsonify({"message":"Event Doesnot Exist"}),404
    else:
        return jsonify({"message":"unAuthenticated user"}),401


@app.route("/events/viewEventsByUserId",methods=["GET"])
@jwt_required
def getEventsByUserId():
    current_user=get_jwt_identity()
    if not current_user:
        return jsonify({"message":"UnAthenticated User"}),403
    else:
        user=db.session.query(userInfo).filter_by(user_name=current_user).first()
        if user:
            events=db.session.query(EventInfo).filter_by(user_id=user.id)
            if events:
                return jsonify(event=[i.serialize for i in events])

@app.route('/events/deleteEventsById/<int:event_id>',methods=['DELETE'])
@jwt_required
def deleteEventById(event_id):
    current_user=get_jwt_identity()
    if current_user:
        event=request.get_json()
        #event_id = event["event_id"]
        eventById=db.session.query(EventInfo).filter_by(event_id=event_id).first()
        userById=db.session.query(userInfo).filter_by(user_name=current_user).first()
        if eventById and event_id:
            if userById.id==eventById.user_id:
                db.session.delete(eventById)
                db.session.commit()
                return jsonify({"message":"Event Deleted Succesfully"})
            else:
                return jsonify({"message":"UnAuthorized to delete this event"}),401
        elif(not eventById):
            return jsonify({"message":"event doesnot exist"})        
        elif(not event_id):
            return jsonify({"message":"Input cant  be empty"}) 
    else:
        return jsonify({"message":"unAuthenticated user"}),403   


        """
        ######
        Registring to An Event CRUD Operation
        #######
        """
@app.route('/events/registerToEvents',methods=['POST'])
@jwt_required
def registerToEvent():
    current_user=get_jwt_identity()
    if current_user:
        event=request.get_json()
        event_id=event["event_id"]
        seat_number_wanted=event["seat_num"]
        does_event_exist=db.session.query(EventInfo).filter_by(event_id=event_id).first()
        user=db.session.query(userInfo).filter_by(user_name=current_user).first()

        if does_event_exist and user and  seat_num:
            sit_limit=does_event_exist.to_be_accepted_users_num
            registered_user=does_event_exist.registered_users_num
            seat_left=sit_limit-registered_user
            if sit_limit > registered_user and seat_left>=seat_number_wanted:
                #available_sit=(sit_limit - registered_user)
                seat_num=seat_number_wanted
                user_id=user.id

                register= Registered_To_Event(user_id=user_id,
                event_id=event_id,seat_num=seat_num,event_title=does_event_exist.title)
                db.session.add(register)
                try:
                    db.session.commit()
                    temp=does_event_exist.registered_users_num
                    does_event_exist.registered_users_num=temp+seat_num
                    db.session.commit()
                    socket.getaddrinfo('127.0.0.1', 5000)
                    msg=Message("Hello,Check this out",recipients=[user.email],sender='tikusevents@gmail.com')
                    msg.body = "Congats,\nyou are Succesfully Registered to \n " +does_event_exist.title+"\nWhen and When ? --"+ does_event_exist.description + ".\n Please Come Early"        
                    mail.send(msg)
                except psycopg2.Error as e:
                    message = "Database error: " + e + "/n SQL: " + new_user
                    return jsonify({"message":message}),401 #render_template("register.html", message = t_message)
           
                return jsonify({"message":"registerd to an event Succesfully"})#


        else:
            return jsonify({"message":"You are trying to register to unexisting event"}),404
    else:
        return jsonify({"message":"unAuthenticated user"}),403


@app.route('/events/updateEventRegistration',methods=['PUT','GET'])
@jwt_required
def updateRegistrationEvent():
    current_user=get_jwt_identity()
    if current_user:
        event=request.get_json()
        seat_number_wanted=event["seat_num"]
        event_id=event["event_id"]
        if seat_number_wanted:
            event_exist=db.session.query(EventInfo).filter_by(event_id=event_id).first()
            reg_exist=db.session.query(Registered_To_Event).filter_by(event_id=event_id).first()

            if event_exist and reg_exist:
                old_seat_num=reg_exist.seat_num
                sit_limit=event_exist.to_be_accepted_users_num
                registered_user=event_exist.registered_users_num

                registered_user=registered_user-old_seat_num
                seat_left=sit_limit-registered_user

                if sit_limit > registered_user and seat_left>=seat_number_wanted:
                #available_sit=(sit_limit - registered_user)
                    try:
                        seat_num=seat_number_wanted
                        reg_exist.seat_num=seat_num
                        db.session.commit()
                        temp=registered_user + seat_num
                        event_exist.registered_users_num=temp
                        db.session.commit()
                    except Exception as e:
                        message = "Database error: " + e + "/n "
                        return jsonify({"Error":message}),401
                    return jsonify({"message":"you have Updated your Event Registration Succesfully","event":event_exist.serialize,"registered_event":reg_exist.serialize}),201
                else:
                    return jsonify({"message":"No Seat Is available"}),400                 
            else:
                return jsonify({"message":"you are trying to update un existing event"}),404
        else:
            return jsonify({"message":"Please Specify seat_num"}),404    

    else:
        return jsonify({"message":"UnAthenticated User"}),403

@app.route('/events/getRegisteredEventById/<int:id>',methods=["GET"])
@jwt_required
def getRegisteredEventById(id):
    current_user=get_jwt_identity()
    if current_user:
        reg_event=db.session.query(Registered_To_Event).filter_by(id=id).first()
        user=db.session.query(userInfo).filter_by(user_name=current_user).first()
        if reg_event and user:
            user_id=user.id
            event_id=reg_event.event_id
            event_exist=db.session.query(EventInfo).filter_by(event_id=event_id).first()
            if user_id==reg_event.user_id and event_exist:
                return jsonify({"message":"Event and Registration Info","event":event_exist.serialize,"registered_event":reg_event.serialize}),200
            else:
                return jsonify({"message":"You are not registered to this event"})
        else:
            return jsonify({"message":"You dont have registration with this id"}),404
    else:
        return jsonify({"message":"unAuthenticated user"}),401

@app.route('/events/updateEvent',methods=['PUT','GET'])
@jwt_required
def updateEvent():
    current_user=get_jwt_identity()

    if current_user:
        event=request.get_json()
        event_id=event['event_id']
        event_title=event['title']
        event_description=event['description']
        event_ends_on=event['event_ends_on']
        event_begins_on=event['event_begins_on']
        event_deadline=event['event_deadline']
        event_picture=event['event_picture']
        event_seat_limit=event['sit_limit']

        if event_id and (event_picture or event_begins_on or event_title or event_deadline or event_description or event_ends_on or event_seat_limit):
            event_exist=db.session.query(EventInfo).filter_by(event_id=event_id).first()
            user_exist=db.session.query(userInfo).filter_by(user_name=current_user).first()
            if event_exist and user_exist:
                if event_exist.user_id==user_exist.id:
                    if event_title:
                        event_exist.title=event_title
                    if len(event_picture)!=0:
                        event_exist.event_picture=event_picture
                    if len(event_description) != 0:
                        event_exist.description=event_description
                    if len(event_deadline)!=0:
                        event_exist.event_deadline=event_deadline
                    if event_seat_limit !=0:
                        event_exist.to_be_accepted_users_num=event_seat_limit
                    if len(event_begins_on)!=0:
                        event_exist.event_begins_on=event_begins_on
                    if len(event_ends_on)!=0:
                        event_exist.event_ends_on=event_ends_on
                    try:
                        db.session.commit()
                    except Exception as e:
                        message = "Database error: " + e + "/n "
                        return jsonify({"Error":message}),401
                    return jsonify({"message":"you have Updated your Event Succesfully","event":event_exist.serialize}),201
                    
                else:
                    return jsonify({"message":"You Cant edit this event"}),401
            else:
                return jsonify({"message":"Sorry The Event Doesnot Exist"}),404

    else:
        return jsonify({"message":"unAuthenticated User"}),401
            
@app.route('/events/deleteEventRegistration/<int:id>')
@jwt_required
def deleteEventRegistration(id):
    current_user=get_jwt_identity()
    if current_user:
        registered=db.session.query(Registered_To_Event).filter_by(id=id).first()

        if registered:
            seat_num=registered.seat_num
            event_id=registered.event_id
            db.session.delete(registered)
            try:
                event=db.session.query(EventInfo).filter_by(event_id=event_id).first()
                if event:
                    db.session.commit()
                    temp=event.registered_users_num - seat_num
                    event.registered_users_num=temp
                    db.session.commit()
                    return jsonify({"message":"You Have Cancelled ur Registration to this event"}),200
                else:
                    return jsonify({"message":"there is no event exist with this registration","event":event.serialize}),400
            except Exception as e:
                message="there is some error"+ e
                return jsonify({"message":message}),400
        else:
            return jsonify({"message":"Couldnt find registration with this id"})
    else:
        return jsonify({"message":"UnAthenticated User"}),401




@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({'message': 'Hello World!', 'User': 'Test User', 'requesData': request.args.get('abc')})



if __name__ == '__main__':
    app.debug = True
    app.run()
#from routes import register