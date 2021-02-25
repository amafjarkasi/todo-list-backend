"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Tasks
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200


# get all tasks
@app.route('/task', methods=['GET'])
def task_all():
    todos = Tasks.query.all()
    response_body = list(map(lambda x: x.serialize(), todos))
    print(response_body)
    return jsonify(response_body), 200

# # get all tasks
# @app.route('/task/<user>', methods=['GET'])
# def task_user():
#     todos = Tasks.query.all()
#     response_body = list(map(lambda x: x.serialize(), todos))
#     print(response_body)
#     return jsonify(response_body), 200

# post a task
@app.route('/task', methods=['POST'])
def task_add():
    todo = request.json
    body = request.get_json()
    
    new_task = Tasks(label=todo["label"], done=todo["done"], user=todo["user"])
    db.session.add(new_task)
    db.session.commit()
    
    # query all tasks and return
    updated_tasks = Tasks.query.filter_by(user=body["user"])
    response_body = list(map(lambda x: x.serialize(), updated_tasks))
    return jsonify(response_body), 200


# update task for specific task id
@app.route('/task/<int:task_id>', methods=['PUT'])
def task_update(task_id):
    
    body = request.get_json()
    
    updated_task = Tasks.query.get(task_id)
    
    if updated_task is None:
        raise APIException('User not found', status_code=404)
    if "label" in body:
        updated_task.label = body["label"]
    if "done" in body:
        updated_task.done = body["done"]
    db.session.commit()
    
    updated_tasks = Tasks.query.filter_by(user=body["user"])
    response_body = list(map(lambda x: x.serialize(), updated_tasks))
    return jsonify(response_body), 200

# delete a task
@app.route('/task/<user>/<int:task_id>', methods=['DELETE'])
def task_delete(user, task_id):
    delete_task = Tasks.query.get(task_id)
    if delete_task is None:
        raise APIException('Task id not found', status_code=404)
    db.session.delete(delete_task)
    db.session.commit()
    
    updated_tasks = Tasks.query.filter_by(user=user)
    response_body = list(map(lambda x: x.serialize(), updated_tasks))
    return jsonify(response_body), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
