from flask import request, jsonify, make_response, current_app, Blueprint
from flask.ext.login import login_user, login_required, logout_user, abort
from project import utils
from project.services.auth import Auth
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
from bson.objectid import ObjectId
from models.user import getUserID
from models import startup

blueprint = Blueprint(
    'startups', __name__
)

def not_owned(startup_object):
    user_id = getUserID('me')

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    if not startup.is_owner(user_id, startup_object):
        return '{}', HTTP_401_NOT_AUTHORIZED

    return None

@blueprint.route('/startups', methods=['POST'])
@Auth.require(Auth.USER)
def create_startup():
    user_id = getUserID('me')
    try:
        new_startup = startup.create_startup(user_id, request.get_json())
        return jsonify(startup.get_basic_startup(new_startup, getUserID('me')))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@blueprint.route('/startups/<startup_id>', methods=['GET'])
@Auth.require(Auth.USER)
def get_basic_startup(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    try:
        return jsonify(startup.get_basic_startup(startup_object, getUserID('me')))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@blueprint.route('/startups/<startup_id>/details', methods=['GET'])
@Auth.require(Auth.USER)
def get_details(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)
    user_id = getUserID('me')

    if startup_object is None:
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    try:
        return jsonify(startup.get_details(startup_object, user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@blueprint.route('/startups/<startup_id>', methods=['PUT'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/wall', methods=['POST'])
@Auth.require(Auth.USER)
def post_wall(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    user_id = getUserID('me')
    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        return jsonify(startup.post_wall(startup_object, request.get_json(), user_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST

@blueprint.route('/startups/<startup_id>/details/wall/<post_id>', methods=['DELETE'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/qa', methods=['POST'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/qa/<question_id>', methods=['PUT'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/qa/<question_id>', methods=['DELETE'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/people', methods=['PUT'])
@Auth.require(Auth.USER)
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

@blueprint.route('/startups/<startup_id>/details/overview', methods=['PUT'])
@Auth.require(Auth.USER)
def update_overview(startup_id):
    startup_object = startup.find_startup_by_id(startup_id)

    no = not_owned(startup_object)
    if not no is None:
        return no

    try:
        startup.put_overview(startup_object, request.get_json())
        return '{}'
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
