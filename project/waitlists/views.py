__author__ = 'austinstone'

from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND
from models import waitlist
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

waitlists_blueprint = Blueprint(
    'waitlists', __name__
)


@waitlists_blueprint.route(ROUTE_PREPEND+'/waitlist', methods=['GET'])
@login_required
def get_waitlist():
    '''
    Gets all the entries in the waitlist sorted by ascending date.
    '''
    try:
        output = []
        cursor = waitlist.find_multiple_waitlists({})
        for entry in cursor:
            output.append(waitlist.get_waitlist_attributes(entry))

        return jsonify(error=None, waitlist=output)
    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST



@waitlists_blueprint.route(ROUTE_PREPEND+'/waitlist', methods=['PUT'])
def create_waitlist_entry():
    '''
    Put an entry into the waitlist. Requires email, firstName, and lastName fields. This endpoint is not
    login required.
    '''
    try:
        req = request.json
        waitlist_entry = waitlist.create_waitlist(req)
        return jsonify(error=None, created=True)

    except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error, created=False), HTTP_400_BAD_REQUEST

