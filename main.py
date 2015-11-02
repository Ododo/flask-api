from flask import Flask, jsonify, abort, make_response, request
from database import db, User, Exercise, Docker, Token
import docker

app = Flask(__name__)

#parameters
debugStatus = True

# MySQL config
db_username='flask'
db_password='flask_pw'
db_hostname='127.0.0.1:3306'
db_name='api_docker'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+db_username+':'+db_password+'@'+db_hostname+'/'+db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

# ============
# | API ROOT |
# ============

@app.route("/")
def root():
	""" Defines basic info for the API """
	return jsonify({
		'title': "Hack in TN api",
		'version': "0.4b",
		'help': "/doc.html"})

# ============
# | INIT API |
# ============

@app.route("/init", methods=["POST"])
def init():
	""" Initialize database """
	db.create_all()
	return jsonify({'status': "Initialization complete"})

@app.route("/coffee", methods=["POST", "PUT", "GET", "DELETE"])
def coffee():
	return make_response(jsonify({'error': "I'm a teapot"}), 418)

# ==============
# | API : USER |
# ==============

# LIST
@app.route("/user/", methods=["GET"])
def list_user():
	""" List all users from <begin> to <length> """
	begin = 0
	length = 25
	try:
		if request.json != None:
			begin = int(request.json.get('begin', 0))
			length = int(request.json.get('length', 25))
	except:
		abort(403)
	if length > 100 :
		length = 100
	userList = User.list(begin, length)
	if userList == None:
		abort(400)
	return jsonify({'users': map(lambda(e): e.output(), userList), 'begin': begin, 'length': length})

# POST
@app.route("/user/", methods=["POST"])
def post_user():
	""" Add user <user_id> to database """
	user = User.add(request.json)
	if user == None:
		abort(404)
	return jsonify({'user': user.output()})

# GET
@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
	""" Retrieves user <user_id> data """
	user = User.get(user_id)
	if user == None:
		abort(404)
	return jsonify({'user': user.output()})

# PUT
@app.route("/user/<int:user_id>", methods=["PUT"])
def put_user(user_id):
	return jsonify({'status': 'Not implemented'}), 501

# DELETE
@app.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
	if Token.invalid(user_id, request.path, request.json):
		if not Token.isLevel(request.path, request.json, Level.ADMIN):
			abort(403)
	User.delete(user_id)
	return jsonify({'status': 'Deleted'}), 402

# ==========================
# | API : USER -> EXERCISE |
# ==========================

# LIST
@app.route("/user/<int:user_id>/exercise/", methods=["GET"])
def user_list_exercises(user_id):
	begin = 0
	length = 25
	try:
		if request.json != None:
			begin = int(request.json.get('begin', 0))
			length = int(request.json.get('length', 25))
	except:
		abort(403)
	try :
		user = User.get(user_id)
	except Exception:
		abort(404);
	exerciseList = user.getExerciseList(begin, length);
	if exerciseList == None:
		abort(400)
	return jsonify({'user': user_id, 'exercises': exerciseList})

# POST
@app.route("/user/<int:user_id>/exercise/", methods=["POST"])
def post_user_exercises(user_id):
	if Token.checkValid(user_id, request.path, request.json) == False:
		abort(403)
	try:
		ex_id = request.json['exercise']
	except Exception:
		abort(400)
	uuid = Docker.add(user_id, ex_id)
	return jsonify({'user': user_id,'exercise': ex_id, 'path': "/ex/"+addAct.uuid}), 201

# GET
@app.route("/user/<int:user_id>/exercise/<int:ex_id>", methods=["GET"])
def get_user_exercises(user_id, ex_id):
	if Token.invalid(user_id, request.path, request.json):
		abort(403)
	user = User.get(user_id)
	if user == None:
		abort(404)
	exercise = user.getExercise(ex_id)
	if exercise == None:
		abort(404)
	return jsonify(exercise)

# DELETE
@app.route("/user/<int:user_id>/exercise/<int:ex_id>", methods=["DELETE"])
def delete_user_exercice(user_id, ex_id):
	if Token.invalid(user_id, request.path, request.json):
		abort(403)
	delAct = users.delExercise(user_id, ex_id)
	if delAct.status == 404:
		abort(404)
	try:
		nginx.delete_nginx(delAct.uuid)
		delete_docker(delAct.did)
		delAct.delete()
	except Exception:
		abort(500)
	return jsonify({'status': "Deleted"}), 202

# ==================
# | API : Exercise |
# ==================

# LIST
@app.route("/exercise/", methods=["GET"])
def exercise_list():
	begin = 0
	length = 25
	try:
		if request.json != None:
			begin = int(request.json.get('begin', 0))
			length = int(request.json.get('length', 25))
	except:
		abort(403)
	data = Exercise.list(begin, length)
	return jsonify(data)


# POST
@app.route("/exercise/", methods=["POST"])
def post_exercise():
	pass

# GET
@app.route("/exercise/<int:ex_id>", methods=["GET"])
def get_exercise(ex_id):
	data = Exercise.get(ex_id)
	if data == None:
		abort(404)
	return jsonify(data)

# ==============
# ERROR HANDLING
# ==============

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': "Bad request"}), 400)

@app.errorhandler(403)
def not_found(error):
	return make_response(jsonify({'error': "Forbidden or not authentificated"}), 403)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': "Not found"}), 404)

@app.errorhandler(409)
def duplicate_entry(error):
	return make_response(jsonify({'error': "Trying to duplicate entry"}), 409)

@app.errorhandler(500)
def server_error(error):
	return make_response(jsonify({'error': "Server error"}), 500)



if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=debugStatus)



