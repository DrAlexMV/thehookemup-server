from flask import request, Blueprint, request, jsonify, make_response, current_app
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND, utils
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
from bson.objectid import ObjectId
from models.user import getUserID
from models import startup

startups_blueprint = Blueprint(
    'startups', __name__
)

def not_owned(startup_object):
    user_id = getUserID('me')

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    if not startup.is_owner(user_id, startup_object):
        return '{}', HTTP_401_NOT_AUTHORIZED

    return None

@startups_blueprint.route(ROUTE_PREPEND+'/startup', methods=['POST'])
@login_required
def create_startup():
    user_id = getUserID('me')
    try:
        new_startup = startup.create_startup(user_id, request.get_json())
        return jsonify(startup.get_basic_startup(new_startup, getUserID('me')))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>', methods=['GET'])
@login_required
def get_basic_startup(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    try:
        return jsonify(startup.get_basic_startup(startup_object, getUserID('me')))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details', methods=['GET'])
@login_required
def get_details(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)
    user_id = getUserID('me')

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    try:
        return jsonify(startup.get_details(startup_object, user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>', methods=['PUT'])
@login_required
def update_basic_startup(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)
    user_id = getUserID('me')

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.update_basic_startup(startup_object, request.get_json())
        return jsonify(startup.get_basic_startup(startup_object, user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/wall', methods=['POST'])
@login_required
def post_wall(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    user_id = getUserID('me')
    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.post_wall(startup_object, request.get_json(), user_id)
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/wall/<post_id>', methods=['DELETE'])
@login_required
def remove_wall(startup_id, post_id):
    startup_object = startup.find_startup_by_id(startup_id)

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.remove_wall(startup_object, post_id, request.get_json())
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/qa', methods=['POST'])
@login_required
def add_question(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)
    user_id = getUserID('me')

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    try:
        startup.add_question(startup_object, request.get_json(), user_id)
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/qa/<question_id>', methods=['PUT'])
@login_required
def give_answer(startup_id, question_id):
    startup_object = startup.find_startup_by_id(startup_id)

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.give_answer(startup_object, question_id, request.get_json())
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/qa/<question_id>', methods=['DELETE'])
@login_required
def delete_question(startup_id, question_id):
    startup_object = startup.find_startup_by_id(startup_id)

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.remove_question(startup_object, question_id, request.get_json())
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@startups_blueprint.route(ROUTE_PREPEND+'/startup/<startup_id>/details/people', methods=['PUT'])
@login_required
def update_people(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.put_people(startup_object, request.get_json())
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
