from flask import Blueprint, request, jsonify
from flask_api.status import HTTP_400_BAD_REQUEST
from pymongo.errors import DuplicateKeyError
from models import admin
from bson.json_util import dumps
from project.services.auth import Auth
from project.strings import resource_strings

blueprint = Blueprint(
    "admins", __name__
)


@blueprint.route('/admins', methods=['POST'])
@Auth.require(Auth.ADMIN)
def create_new_admin():
    try:
        user_id = request.get_json()["user"]
        new_admin_settings = admin.create_admin_settings(user_id)
        return jsonify(new_admin_settings)
    except DuplicateKeyError:
        return jsonify({"error": resource_strings['DUP_EMAIL']}), HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@blueprint.route('/admins/unactivated', methods=['GET'])
@Auth.require(Auth.ADMIN)
def get_unactivated_users():
    try:
        unactivated_users = admin.find_unactivated_users()
        return jsonify({"users": unactivated_users})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST
