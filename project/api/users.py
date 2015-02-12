from flask import redirect, render_template, request, \
    url_for, Blueprint, jsonify, session, Response
from project import utils, database_wrapper
from project.services.auth import Auth
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
from models import user
from bson.objectid import ObjectId
import sys
import json

blueprint = Blueprint(
    'users', __name__
)

@blueprint.route('/users/<user_id>', methods=['PUT'])
@Auth.require(Auth.USER)
@Auth.only_me
def user_basic_info(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND

    req = request.get_json()
    try:
        utils.mergeFrom(req, entry, user.User.basic_info_fields, require=False)
        database_wrapper.save_entity(entry)
    except:
        return jsonify(error='Invalid key'), HTTP_400_BAD_REQUEST
    return '', HTTP_200_OK


@blueprint.route('/users/<user_id>', methods=['GET'])
@Auth.require(Auth.USER)
def userBasicInfo(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND
    return user.get_basic_info_with_security(entry)

@blueprint.route('/users/<user_id>/<attribute>', methods=['DELETE'])
@Auth.require(Auth.USER)
@Auth.only_me
def delete_basic_user_info(user_id, attribute):
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND
    try:
        entry[attribute] = None
        database_wrapper.save_entity(entry)
    except:
        print sys.exc_info()[0]
        return jsonify(error='Invalid key or field cannot be deleted'), HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
    return '', HTTP_200_OK


@blueprint.route('/users/<user_id>/details', methods=['GET'])
@Auth.require(Auth.USER)
def get_user_details(user_id):
    try:
        entry = user.findUserByID(user_id)
        if entry is None:
            return '', HTTP_404_NOT_FOUND
        return user.get_user_details(entry, user_id == 'me')
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@blueprint.route('/users/<user_id>/details/initialization', methods=['PUT'])
@Auth.require(Auth.USER)
@Auth.only_me
def put_initialization(user_id):
    req = request.get_json()
    user_object = user.findUserByID(user_id)
    user.set_initialization_level(user_object, req['initialization'])
    return jsonify(error='')

@blueprint.route('/users/<user_id>/details/skills', methods=['PUT'])
@Auth.require(Auth.USER)
@Auth.only_me
def put_skills(user_id):
    """
    Example request:

    PUT
    {
    "skills":["javascript"]
    }

    returns STATUS_200_OK when successful
    """
    req = request.get_json()
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND
    if user.put_skills(entry, req):
        return '', HTTP_200_OK
    else:
        return '', HTTP_400_BAD_REQUEST


@blueprint.route('/users/<user_id>/details/interests', methods=['PUT'])
@Auth.require(Auth.USER)
@Auth.only_me
def put_interests(user_id):
    """
    Example request:

    PUT
    {
     "interests":[{"title":"some title", "description":"some description"},
               {"title":"some title 2", "description":"some description 2"}]
    }

    returns STATUS_200_OK when successful
    """
    req = request.get_json()
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND
    if user.put_interests(entry, req):
        return '', HTTP_200_OK
    else:
        return '', HTTP_400_BAD_REQUEST

@blueprint.route('/users/<user_id>/details/projects', methods=['PUT'])
@Auth.require(Auth.USER)
@Auth.only_me
def put_projects(user_id):
    """
    Example request:

    PUT
    {
    "projects":[{
            "date": "May 2015",
            "title": "some project title",
            "description": "some project description",
            "details": [{
                "title": "some project detail title",
                "description": "some project detail description"
                        }],
            "people":["54b797090adfa96230c2c1bb"]
        }]
    }

    returns status 200_OK when successful
    """
    req = request.get_json()
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND
    if user.put_projects(entry, req):
        return '', HTTP_200_OK
    else:
        return '', HTTP_400_BAD_REQUEST

@blueprint.route('/users/<user_id>/edges', methods=['GET'])
@Auth.require(Auth.USER)
def userEdges(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        return '', HTTP_404_NOT_FOUND

    suggested_connections = []
    pending_connections = []
    pending_connections_messages = {}

    if user_id == 'me':
        suggested_connection_users = user.get_suggested_connections(entry)
        suggested_connections = user.get_basic_info_from_users(suggested_connection_users)

        pending_connection_ids = map(lambda connection : ObjectId(connection['user']),
                                     user.get_pending_connections(entry))

        pending_connections = user.get_basic_info_from_ids(pending_connection_ids)

        map(lambda connection: pending_connections_messages.update({connection['user']:connection['message']}),
            user.get_pending_connections(entry))

    connection_ids = map(ObjectId, user.get_connections(entry))
    connections = user.get_basic_info_from_ids(connection_ids)

    annotated = {'connections': connections,
                 'suggestedConnections': suggested_connections,
                 'pendingConnections': pending_connections,
                 'pendingConnectionsMessages': pending_connections_messages,
                 'associations': []}

    return jsonify(**annotated)

@blueprint.route('/users/<user_id>/edges/connections', methods=['POST'])
@Auth.require(Auth.USER)
@Auth.only_me
def add_connection_route(user_id):
    req = request.get_json()

    # TODO: have some system so friend requests are sent
    connection_id = req.get('user')
    connection_message = req.get('message')

    if connection_id is None:
        return jsonify(error='missing field \'user\''), HTTP_400_BAD_REQUEST

    other_user = user.findUserByID(connection_id)

    if other_user is None:
        return jsonify(error='bad user'), HTTP_400_BAD_REQUEST

    try:
        ## TODO: improve specificity of errors
        user.handle_connection(other_user, connection_message)
        return '{}', HTTP_200_OK
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@blueprint.route('/users/<user_id>/edges/connections/<connection_id>', methods=['DELETE'])
@Auth.require(Auth.USER)
@Auth.only_me
def remove_connection_route(user_id, connection_id):
    entry = user.findUserByID(user_id)
    connection = user.findUserByID(connection_id)
    if entry is None or connection is None:
        return '', HTTP_404_NOT_FOUND

    try:
        ## TODO: improve specificity of errors
        user.remove_user_connection(connection)
        return '{}', HTTP_200_OK
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR
