from flask import redirect, request, url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import utils, database_wrapper
from project.services.auth import Auth
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
from models import user, invite
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

blueprint = Blueprint(
    'invites', __name__
)


@blueprint.route('/invites', methods=['GET'])
@Auth.require(Auth.USER)
def get_invites():
    '''
    Gets all the invites for the currently logged on user
    '''
    user_id = user.getUserID('me')
    entries = invite.find_multiple_invites({'producerObjectId': user_id})
    invite_attributes_list = [invite.get_invite_attributes(entry) for entry in entries]
    return jsonify(error=None, invites=invite_attributes_list)


@blueprint.route('/invites/<invite_id>', methods=['PUT'])
@Auth.require(Auth.USER)
def put_invite(invite_id):
    invite.put_invite(invite_id, request.get_json())
    return jsonify(error=None)


# This endpoint needs to be removed before release
@blueprint.route('/invites/create', methods=['POST'])
@Auth.require(Auth.USER)
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


@blueprint.route('/invites/validate/<invite_code>', methods=['GET'])
def validate_invite(invite_code):
    if invite.is_valid(invite_code):
        return jsonify(error=None, status=True)
    else:
        return jsonify(error='Invalid Code', status=False), HTTP_400_BAD_REQUEST
