from flask import Blueprint, request, jsonify
from project import ROUTE_PREPEND
from models import endorsement, user
from flask_api.status import HTTP_400_BAD_REQUEST
from flask_login import login_required
from bson.json_util import dumps

endorsements_blueprint = Blueprint('endorsements', __name__)


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/<entity_id>/endorsees', methods=['GET'])
@login_required
def entity_endorsees(entity_id):
    try:
        endorsees = endorsement.endorsees(entity_id=entity_id)
        endorsees_basic_info = endorsement.find_entity_list_by_type(endorsees)
        return dumps({'endorsees': endorsees_basic_info})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/<entity_id>/endorsers', methods=['GET'])
@login_required
def entity_endorsers(entity_id):
    try:
        endorsers = endorsement.endorsers(entity_id=entity_id)
        endorsers_basic_info = endorsement.find_entity_list_by_type(endorsers)
        return dumps({'endorsers': endorsers_basic_info})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/<entity_id>/count', methods=['GET'])
@login_required
def endorsements_count(entity_id):
    try:
        return dumps(endorsement.count(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}, HTTP_400_BAD_REQUEST)


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/<entity_id>', methods=['GET'])
@login_required
def all_endorsements(entity_id):
    try:
        return dumps(endorsement.find_endorsements_by_id(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/me', methods=['POST'])
@login_required
def add_user_endorsee():
    try:
        entity = request.get_json()
        user_endorsees = endorsement.endorse_entity(entity['id'], entity['entityType'])
        return dumps({'endorsees': user_endorsees})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/me/<entity_id>', methods=['DELETE'])
@login_required
def remove_endorsement(entity_id):
    try:
        return dumps(endorsement.user_remove_endorsement(entity_id=entity_id))
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST


@endorsements_blueprint.route(ROUTE_PREPEND + '/endorsement/<endorser_id>/<endorsee_id>', methods=['GET'])
@login_required
def has_entity_endorsed(endorser_id, endorsee_id):
    try:
        return dumps({'hasEndorsed': endorsement.has_entity_endorsed(endorsee_id, entity_id=endorser_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), HTTP_400_BAD_REQUEST





