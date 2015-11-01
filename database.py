from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from passlib.hash import bcrypt
import binascii, os

app_secret_salt = "12345678901234567890AB"
exptime = timedelta(hours=12)
db = SQLAlchemy()

def encrypt_pass(password):
	return bcrypt.encrypt(password, salt=app_secret_salt)
	
def hash_command(token, url, json):
	oneline = url + '\\' + json
	return bcrypt.encrypt(oneline, salt=token)

def generate_token():																							
	return binascii.hexlify(os.urandom(22))

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(256))
	email = db.Column(db.String(256), unique=True)
	level = db.Column(db.Integer)
	creation_date = db.Column(db.DateTime)
	
	def __init__(self, username, password, email):
		self.username = username
		self.password = encrypt_pass(password)
		self.email = email
		self.level = 1
		self.creation_date = datetime.utcnow()
	
	@staticmethod
	def getUserList(begin = 0, length = 25):
		return User.query.order_by(User.creation_date.asc()).limit(length).offset(begin).all()
		
	@staticmethod
	def getUser(user_id):
		return User.query.filter(User.id == user_id).first()
		
	@staticmethod
	def add(json):
		try:
			print "Checking for user email..."
			checker = User.query.filter(User.email == json['email']).first()
			print "Is user email already in DB ? ("+json['email']+")"
			if checker != None:
				abort(409)
			print "Creating user "+json['username']
			newUser = User(json['username'], json['password'], json['email'])
			print "Created user "+json['username']
			db.session.add(newUser)
			print "Added user "+json['username']+" to database"
		except Exception:
			abort(400)
		

class Exercise(db.Model):
	__tablename__ = 'exercise'
	id = db.Column(db.Integer, primary_key=True)
	ex_id = db.Column(db.String(64), unique = True)
	docker_name = db.Column(db.String(64))

class Docker(db.Model):
	__tablename__ = 'docker'
	id = db.Column(db.Integer, primary_key=True)
	ex_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	key = db.Column(db.String(80), nullable = True)
	uuid = db.Column(db.String(80), nullable = True, unique = True)
	launched = db.Column(db.DateTime)
	valid = db.Column(db.Boolean)
	def __init__(self, ex_id, user_id, uuid, key):
		self.ex_id = ex_id
		self.user_id = user_id
		self.uuid = uuid
		self.key = key
		self.launched = datetime.utcnow()

class Token(db.Model):
	__tablename__ = 'token'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	token = db.Column(db.String(22))
	expires = db.Column(db.DateTime)
	level = db.Column(db.Integer)
	def __init__(self, user_id):
		self.user_id = user_id
		self.token = generate_token()
		self.expires = datetime.utcnow() + exptime;
		self.level = User.query.filter(User.id == user_id).first().level
	
	@staticmethod
	def checkValid(user_id, url, json):
		token = Token.query.filter(Token.user_id == user_id).order_by(Token.expires.desc()).first()
		if token == None:
			return None
		if token.expires > datetime.utcnow():
			return None
		regenerated = custom_app_context.encrypt(oneline(command, json))
		if regenerated != token:
			return None
		return user
