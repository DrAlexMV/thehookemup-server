from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
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

@invites_blueprint.route(ROUTE_PREPEND+'/invites', methods=['GET'])
@login_required
def get_invites():
    '''
    Gets all the invites for the currently logged on user
    '''
    try:
        user_id = user.getUserID('me')
        entries = invite.find_multiple_invites({'producerObjectId':str(user_id)})
        invite_attributes_list = [invite.get_invite_attributes(entry) for entry in entries]
        return jsonify(error=None, invites=invite_attributes_list)
    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST

@invites_blueprint.route(ROUTE_PREPEND+'/invites/create/<number>', methods=['PUT'])
@login_required
def create_invites(number):
    '''
    Create <number> of invites for the currently logged in user.
    '''
    try:
        user_id = user.getUserID('me')
        entries = invite.find_multiple_invites({'producerObjectId':str(user_id)})
        if entries.count() > 0:
            raise Exception('User already was given invite codes')

        number = int(number)
        output_invites = []
        for i in range(number):
            output_invite = invite.create_invite(user_id)
            output_invites.append(invite.get_invite_attributes(output_invite))
        return jsonify(error=None, invites=output_invites)

    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST


@invites_blueprint.route(ROUTE_PREPEND+'/invites/consume/<invite_code>', methods=['PUT'])
@login_required
def consume_invite(invite_code):
    '''
    Fills in the consumer field of the code with the current userid
    '''
    try:
        request_error = ''
        user_id = str(user.getUserID('me'))
        try:
            invite.consumeInvite(ObjectId(invite_code), user_id)
        except Exception as e:
            return jsonify(error='Invalid code'), HTTP_400_BAD_REQUEST

        return jsonify(error=None)
    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST

@invites_blueprint.route(ROUTE_PREPEND+'/invites/validate/<invite_code>', methods=['GET'])
@login_required
def validate_invite(invite_code):
    '''
    Indicates whether or not a code is valid
    '''
    try:
        try:
            invite_entry = invite.find_invite_by_id(ObjectId(invite_code))
            if invite_entry is None:
                raise Exception('Code not found')
            if invite_entry.consumerObjectId is not None:
                raise Exception('Code already used')

        except Exception as e:
            return jsonify(error='Invalid Code', status=False), HTTP_400_BAD_REQUEST

        return jsonify(error=None, status = True)

    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST