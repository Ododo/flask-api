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

@app.route("/")
def hello():
	return jsonify({
		'title': "Hack in TN api",
		'version': "0.4b",
		'help': "/doc.html"})

@app.route("/init", methods=["POST"])
def init():
	db.create_all()
	return jsonify({'status': "Initialization complete"})

@app.route("/user/", methods=["GET"])
def user_list():
	begin = 0
	try:
		begin = int(request.json['begin'])
	except Exception:
		pass
	length = 25
	try:
		length = int(request.json['length'])
	except Exception :
		pass
	if length > 100 :
		length = 100
	userList = User.getUserList(begin, length)
	if userList == None:
		abort(400)
	return jsonify({'users': userList, 'begin': begin, 'length': length})

@app.route("/user/", methods=["PUT"])
def user_put():
	user = User.add(request.json)
	if user == None:
		abort(404)
	return jsonify({'user': user})

@app.route("/user/<int:user_id>", methods=["GET"])
def user_get(user_id):
	user = User.getUser(user_id)
	if user == None:
		abort(404)
	return jsonify({'user': user})

@app.route("/user/<int:user_id>/exercise/", methods=["GET"])
def user_list_exercises(user_id):
	begin = 0
	try:
		begin = int(request.json['begin'])
	except Exception:
		pass
	length = 25
	try:
		length = int(request.json['length'])
	except Exception :
		pass
	exerciseList = User.getExerciseList(user_id, begin, length);
	if exerciseList == None:
		abort(400)
	if len(exerciseList) == 0 :
		abort(404)
	return jsonify({'user': user_id, 'exercises': exerciseList})

@app.route("/user/<int:user_id>/exercise/<int:ex_id>", methods=["GET"])
def user_get_exercise(user_id, ex_id):
	if Token.checkValid(user_id, request.path, request.json) == False:
		abort(403)
	exercise = users.getExercise(user_id, ex_id)
	if exercise == None:
		abort(404)
	return jsonify(exercise)

@app.route("/user/<int:user_id>/exercise/", methods=["POST"])
def user_add_exercice(user_id):
	if Token.checkValid(user_id, request.path, request.json) == False:
		abort(403)
	try:
		ex_id = request.json['exercise']
	except Exception:
		abort(400)
	addAct = users.addExercise(user_id, ex_id)
	if addAct.status >= 400 :
		abort(addAct.status)
	did = docker.createDocker(ex_id)
	nginx.make_config_file(addAct.uuid, did)
	addAct.did = did
	db.session.add(addAct)
	return jsonify({'user': user_id,'exercise': ex_id, 'path': "/ex/"+addAct.uuid}), 201
	
@app.route("/user/<int:user_id>/exercise/<int:ex_id>", methods=["DELETE"])
def user_del_exercice(user_id, ex_id):
	if Token.checkValid(user_id, request.path, request.json) == False:
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
def not_found(error):
	return make_response(jsonify({'error': "Trying to duplicate entry"}), 409)

@app.errorhandler(500)
def server_error(error):
	return make_response(jsonify({'error': "Server error"}), 500)



if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=debugStatus)



