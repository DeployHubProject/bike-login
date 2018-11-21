#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""This script runs the backend CRUD for login and user list."""

#
# Copyright (c) 2018 DeployHub, Inc
#
# This file is part of DeployHub Project
# ( see https://www.deployhubproject.io).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import pprint
import os
from flask import Flask, jsonify, request, abort, make_response
from pymongo import MongoClient, errors 
from bson.objectid import ObjectId
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

db = None
dburl = 'mongodb://' + os.getenv('BIKE_DB_SERVICE_HOST','docker.for.mac.localhost') + ':27017'
    pprint.pprint(client.server_info())
    db = client.test
except errors.ConnectionFailure as e:
    print ("Could not connect to server: %s") % e

    
@app.route('/users', methods=['GET'])
def get_users():
    """return a list of user objects.
    Get the list of all users."""

    response_object = []

    for user in db.users.find():
        user['id'] = str(user.pop('_id'))
        response_object.append(user)
    return jsonify(response_object)


@app.route('/users/register', methods=['POST'])
def register():
    """return a new registered user object.  Error if user is already defined.
    Register the user if the username is not taken."""

    response_object = {}
    user = request.get_json()
    found_user = db.users.find_one({'username': user['username']})

    if (found_user is not None and found_user['username'] == user['username']):
        abort(return_error('Username "' + user['username'] + '" is already taken'))

    _id = str(db.users.insert_one(user).inserted_id)
    response_object['id'] = _id
    return jsonify(response_object)


@app.route('/users/authenticate', methods=['POST'])
def authenticate():
    """return the user object and JWT when login is successfull otherwise an error.
    Login process."""

    response_object = {}
    user = request.get_json()
    found_user = db.users.find_one({'username': user['username']})

    if (found_user is None):
        abort(return_error('User "' + user['username'] + '" not found'))

    if (found_user['password'] != user['password']):
        abort(return_error('Invalid Password'))
    response_object = found_user
    response_object['id'] = str(response_object.pop('_id'))
    response_object['token'] = 'fake-jwt-token'
    return jsonify(response_object)


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    """return a user object for a specific _id.
    Get a specific user based on _id."""

    response_object = {}
    found_user = db.users.find_one({'username': username})

    if (found_user is None):
        return jsonify(response_object)

    response_object = found_user
    response_object['id'] = str(response_object.pop('_id'))
    return jsonify(response_object)


@app.route('/users/<userid>', methods=['PUT'])
def update_user(userid):
    """return the updated user object.
    Update a user."""

    response_object = {}
    user = request.get_json()
    user['_id'] =  ObjectId(userid)
    r = db.users.replace_one({'_id': ObjectId(userid)}, user)
    pprint.pprint(r.matched_count)
    pprint.pprint(r.modified_count)
    response_object = user
    response_object['id'] = str(response_object.pop('_id'))
    return jsonify(response_object)


@app.route('/users/<userid>', methods=['DELETE'])
def del_user(userid):
    """return empty response on delete.
    Delete a user."""

    response_object = {}
    db.users.delete_one({'_id': ObjectId(userid)})
    return jsonify(response_object)

def return_error(message):
    response = jsonify({'message': message})
    response.status_code = 400
    return response
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
