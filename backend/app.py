from flask import Flask, Response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from async_read import create_files, async_read_files
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
auth = HTTPBasicAuth()

db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)


# MODELS
class Permissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey(
        "permissions.id"), nullable=False)

    def __init__(self, name, password_hash, permission_id):
        self.name = name
        self.password_hash = password_hash
        self.permission_id = permission_id


# Creating database and seed with admin and user
db.drop_all()
db.create_all()
db.session.add(Permissions("full"))
db.session.add(Permissions("read"))
db.session.add(Users("admin", generate_password_hash("admin"), 1))
db.session.add(Users("user", generate_password_hash("user"), 2))
db.session.commit()

# Creating json files (for async reads)
create_files()


# AUTH MIDDLEWARE
@auth.verify_password
def verify_password(username, password):
    user = Users.query.filter_by(name=username).first()
    if not user:
        return False
    return check_password_hash(user.password_hash, password)


def admin_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        user = Users.query.filter_by(name=auth.username).first()
        role = Permissions.query.get(user.id)
        if not role.name == 'full':
            return Response('FORBIDDEN', 403)
        return f(**kwargs)
    return wrapped_view


# ROUTES

# get one user
@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    user = Users.query.get(id)
    if not user:
        return Response(f"userid {id} does not exists", 404)
    del user.__dict__['_sa_instance_state']
    del user.__dict__['password_hash']
    return jsonify(user.__dict__)


# get all users
@app.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    items = []
    for item in db.session.query(Users).all():
        del item.__dict__['_sa_instance_state']
        del item.__dict__['password_hash']
        items.append(item.__dict__)
    return jsonify(items)


# create new user
@app.route('/users', methods=['POST'])
@auth.login_required
@admin_required
def create_user():
    body = request.get_json()
    permission = Permissions.query.get(body['permission_id'])
    if not permission:
        return Response(f"invalid permission id {body['permission_id']}", 400)
    db.session.add(Users(body['name'], generate_password_hash(body['password']),
                         body['permission_id']))
    db.session.commit()
    return "user created"


# update existing user
@app.route('/users/<id>', methods=['PUT'])
@auth.login_required
@admin_required
def update_user(id):
    body = request.get_json()
    user = Users.query.get(id)
    if not user:
        return Response(f"userid {id} does not exists", 404)

    if 'name' in body:
        user.name = body['name']
    if 'password' in body:
        user.password = generate_password_hash(body['password'])
    if 'permission_id' in body:
        user.permission_id = body['permission_id']
    db.session.commit()
    return "user updated"


# delete user
@app.route('/users/<id>', methods=['DELETE'])
@auth.login_required
@admin_required
def delete_user(id):
    user = Users.query.get(id)
    if not user:
        return Response(f"userid {id} does not exists", 404)
    db.session.query(Users).filter_by(id=id).delete()
    db.session.commit()
    return "user deleted"


# get all permissions
@app.route('/permissions', methods=['GET'])
@auth.login_required
def get_permissions():
    items = []
    for item in db.session.query(Permissions).all():
        del item.__dict__['_sa_instance_state']
        items.append(item.__dict__)
    return jsonify(items)


# read data asynchronously
@app.route('/data', methods=['get'])
@auth.login_required
async def get_data():
    # reading from files
    result = await async_read_files()

    # filtering out exceptions
    data = [i for i in result if type(i) == list]

    # merging lists
    data = list(itertools.chain.from_iterable(data))

    # returning sorted res
    return jsonify(sorted(data, key=lambda r: r['id']))
