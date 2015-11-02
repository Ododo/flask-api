from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from enum import Enum
import docker, nginx
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

class Level(Enum):
	UNID = 0
	ID = 1
	ADMIN = 4

# =================
# |				  |
# | USER DATABASE |
# |				  |
# =================


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
		self.level = Level.UNID
		self.creation_date = datetime.utcnow()
		
	@staticmethod
	def list(begin = 0, length = 25):
		""" Return an user list, ordered by ID, from <begin> to <length> """
		return User.query.order_by(User.creation_date.asc()).limit(length).offset(begin).all()
		
	@staticmethod
	def get(user_id):
		""" Returns the Database user <user_id> """
		return User.query.filter(User.id == user_id).first()
		
	@staticmethod
	def add(json):
		try:
			checker = User.query.filter(User.email == json['email']).first()
		except Exception:
			abort(500)
		if checker != None:
			abort(409)
		try :
			newUser = User(json['username'], json['password'], json['email'])
			db.session.add(newUser)
			db.session.commit()
		except Exception:
			abort(500)
		return newUser
	
	
	def getExerciseList(self, begin = 0, limit = 25):
		try :
			list = Exercise.query.outerjoin(Docker).filter(Docker.user_id == self.id).limit(limit).offset(begin).all();
		except Exception:
			abort(500);
		return list;
			
			
	def getExercise(self, ex_id):
		try :
			exercise = Docker.query.select(Docker.user_id == self.id, Docker.ex_id == ex_id);
		except Exception:
			abort(500);
		try :
			exercise = exercise.first();
			if exercise == None:
				raise Exception
		except Exception:
			return {
				'exercise': ex_id,
				'user': self.id,
				'launched': False,
				'valid': False
			}
		else:
			return {
				'exercise': ex_id,
				'user': self.id,
				'launched': exercise.launched,
				'valid': exercise.valid
			}
	
	def output(self):
		return {
			'username': self.username,
			'id': self.id,
			'email': self.email
		}
		


# =====================
# |					  |
# | EXERCISE DATABASE |
# |					  |
# =====================

class Exercise(db.Model):
	__tablename__ = 'exercise'
	id = db.Column(db.Integer, primary_key=True)
	ex_id = db.Column(db.String(64), unique = True)
	docker_name = db.Column(db.String(64))

	def __init__(self, ex_id, docker_name):
		self.ex_id = ex_id
		self.docker_name = docker_name

	def add(json):
		try:
			print "Checking for duplicates"
			checker = Exercise.query.filter(Exercise.docker_name == json['docker_name']).first()
			if checker != None:
				abort(409)
			print "Creating exercise"
			newExercise = Exercise(json['exercise'], json['docker_name'])
			print "Adding exercise to DB"
			db.session.add(newExercise)
		except Exception:
			abort(400)
		return newExercise
	
	def list(begin = 0, length = 25):
		return Exercise.query.order_by(Exercise.id).limit(length).offset(begin).all()
		
	def get(ex_id):
		Exercise.query.select(Exercise.id == ex_id).first()



# ===================
# |				    |
# | Docker DATABASE |
# |				    |
# ===================

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
		self.valid = False
	def add(user_id, ex_id):
		try :
			print "Checking for " + ex_id + '\'s docker name'
			docker_name = Exercise.query.filter(Exercise.ex_id == ex_id).select(Exercise.docker_name).first()['docker_name']
			print "Checking for duplicates for docker pair " + user_id + " / " + ex_id
			checker = Docker.query.filter(Docker.user_id == user_id).filter(Docker.ex_id == ex_id).first()
			if checker != None:
				abort(409)
			print "Creating new container for user " + user_id + "based on image " + ex_id
			# TODO check UUID creation + key creation.
			uuid = "TODO_CREATE_UUID"
			key = "TODO_CREATE_KEY"
			d_id = create_docker(docker_name)
			newDocker = Docker(ex_id, user_id, uuid, key)
			print "Saving Docker data and relaoding NGINX"
			create_config_file(uuid, d_id)
			db.session.add(newDocker)
			reload_nginx()
		except Exception :
			abort(500)
		return uuid
	
	def rem(self):
		try :
			print "Removing container " + self.uuid
			print "Removing config file"
			nginx.del_config_file(self.uuid)
			print "Closing docker"
			docker.stop_docker(self.d_id)
			print "Deleting entry"
			db.session.remove(self)
		except Exception:
			abort(500)
			


# ==================
# |				   |
# | TOKEN DATABASE |
# |				   |
# ==================

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
	def invalid(user_id, url, json):
		token = Token.query.filter(Token.user_id == user_id).order_by(Token.expires.desc()).first()
		if token == None:
			return None
		if token.expires > datetime.utcnow():
			return None
		del json['token']
		regenerated = custom_app_context.encrypt(oneline(url, json))
		if regenerated != token:
			return None
		return user
	
	@staticmethod
	def isLevel(url, json, level):
		try :
			user_id = json['user_id']
			user_token = json['token']
		except Exception:
			return False
		token = Token.query.filter(Token.user_id == user_id).order_by(Token.expires.desc()).first()
		if token == None:
			return None
		if token.expires > datetime.utcnow():
			return None
		del json['token']
		regenerated = custom_app_context.encrypt(oneline(url, json))
		if regenerated != user_token:
			return None
		return user
