from flask import Blueprint, request, jsonify
from project import ROUTE_PREPEND
from models import follow
from flask_api.status import HTTP_400_BAD_REQUEST
from flask_login import login_required
from bson.json_util import dumps

follows_blueprint = Blueprint('follows', __name__)


@follows_blueprint.route(ROUTE_PREPEND + '/follow/<entity_id>/followees', methods=['GET'])
@login_required
def entity_followees(entity_id):
    try:
        return dumps({'followees': follow.followees(entity_id=entity_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@follows_blueprint.route(ROUTE_PREPEND + '/follow/<entity_id>/followers', methods=['GET'])
@login_required
def entity_followers(entity_id):
    try:
        return dumps({'followers': follow.followers(entity_id=entity_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@follows_blueprint.route(ROUTE_PREPEND + '/follow/<entity_id>/count', methods=['GET'])
@login_required
def follows_count(entity_id):
    try:
        return dumps(follow.count(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}, HTTP_400_BAD_REQUEST)


@follows_blueprint.route(ROUTE_PREPEND + '/follow/<entity_id>', methods=['GET'])
@login_required
def all_follows(entity_id):
    try:
        return dumps(follow.find_follows_by_id(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@follows_blueprint.route(ROUTE_PREPEND + '/follow', methods=['POST'])
@login_required
def add_user_followee():
    try:
        entity = request.get_json()
        user_followees = follow.follow_entity(entity['id'], entity['type'])
        return dumps({'followees': user_followees})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@follows_blueprint.route(ROUTE_PREPEND + '/follow/<entity_id>', methods=['DELETE'])
@login_required
def unfollow_entity(entity_id):
    try:
        return dumps(follow.user_unfollow(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


