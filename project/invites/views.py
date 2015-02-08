from flask import redirect, request, url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND, utils, database_wrapper
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
from models import user, invite
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

invites_blueprint = Blueprint(
    'invites', __name__
)

@invites_blueprint.route(ROUTE_PREPEND + '/invites', methods=['GET'])
@login_required
def get_invites():
    '''
    Gets all the invites for the currently logged on user
    '''
    user_id = user.getUserID('me')
    entries = invite.find_multiple_invites({'producerObjectId':str(user_id)})
    invite_attributes_list = [invite.get_invite_attributes(entry) for entry in entries]
    return jsonify(error=None, invites=invite_attributes_list)

@invites_blueprint.route(ROUTE_PREPEND + '/invites/<invite_id>', methods=['PUT'])
@login_required
def put_invite(invite_id):
    invite.put_invite(invite_id, request.get_json())
    return jsonify(error=None)

## This endpoint needs to be removed before release
@invites_blueprint.route(ROUTE_PREPEND + '/invites/create', methods=['POST'])
@login_required
def create_invites():
    '''
    Create <number> of invites for the currently logged in user.
    '''

    try:
        user_id = user.getUserID('me')
        number = int(request.get_json()['number'])
        output_invites = []
        for i in range(number):
            output_invite = invite.create_invite(user_id)
            output_invites.append(invite.get_invite_attributes(output_invite))
        return jsonify(error=None, invites=output_invites)
    except Exception as e:
        return jsonify(error=str(e))

@invites_blueprint.route(ROUTE_PREPEND + '/invites/validate/<invite_code>', methods=['GET'])
@login_required
def validate_invite(invite_code):
    '''
    Indicates whether or not a code is valid
    '''
    try:
        invite_entry = invite.find_invite_by_code(ObjectId(invite_code))
        if invite_entry is None:
            raise Exception('Code not found')
        if invite_entry.consumerObjectId is not None:
            raise Exception('Code already used')

    except Exception as e:
        return jsonify(error='Invalid Code', status=False), HTTP_400_BAD_REQUEST

    return jsonify(error=None, status = True)
