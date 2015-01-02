from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND, utils, database_wrapper
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
from models import user
from flask_oauth import OAuth
from bson.objectid import ObjectId
import search_functions
import sys



search_blueprint = Blueprint(
    'search', __name__
)

@search_blueprint.route(ROUTE_PREPEND+'/search', methods=['GET'])
@login_required
def search():
    error = None
    query_string = request.args.get('query_string')
    filter_json = json.loads(request.args.get('filter_json'))
    print query_string
    print filter_json
    try:
        if filter_json == None:
            #call basic search
            results = search_functions.simple_search_users(query_string)
        else:
            #call filtered search
            results = search_functions.filtered_search_users(query_string,filter_json)
    except:
        e = sys.exc_info()[0]
        return jsonify(error=str(e)),HTTP_400_BAD_REQUEST
    return jsonify(results=results, error=None)