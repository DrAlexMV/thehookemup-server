from flask import request, Blueprint, jsonify
from flask.ext.login import login_required
from project import ROUTE_PREPEND, utils
from models import user
from flask.ext.api.status import *
from bson.objectid import ObjectId
import search_functions
import ast


search_blueprint = Blueprint(
    'search', __name__
)



@search_blueprint.route(ROUTE_PREPEND+'/search', methods=['GET'])
@login_required
def search():
    """

    Takes url params as arguments. One of the arguments must be named "query_string". This
    argument is the actual query entered into the search bar. The rest of the arguments are optional
    and can be named anything. These arguments must contain single item json, i.e. {term:filter} where
    term is the name of the field to be filtered, and filter is the required string for that field.
    For example,

    /api/v1/search?query_string=hardware%20java%20ibm&role=programmer&firstName=tanner

    will search for all users that have the words hardware, java, and ibm anywhere in their information,
    and it will then filter those results to only results that have the role set to "programmer" and the
    firstName set to "tanner". Results are returned in the form of a list of json results.

    """
    error = None
    list_filters = []
    try:
        query_string = request.args.get('query_string')
        
        keyed_queries = {}
        for constraint, value in request.args.items():
            if constraint == 'query_string':
                continue

            keyed_queries[constraint] = value.lower()

        if query_string: # disallow empty strings as well as None
            query_string = query_string.lower()

        if keyed_queries:
            results = search_functions.filtered_search_users(query_string, [{'term':keyed_queries}])
        else:
            #call basic search
            results = search_functions.simple_search_users(query_string)

    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST

    ## now turn the queries into basic users
    user_ids = map(ObjectId, (user['_id'] for user in results))
    basic_users = user.get_basic_info_from_ids(user_ids)
    return jsonify(results=basic_users, error=None)



@search_blueprint.route(ROUTE_PREPEND+'/search/autocomplete/skills', methods=['GET'])
@login_required
def autocomplete_skill():
    """

    """
    error = None

    try:
        terms = []
        for param_name, param_value in request.args.items():
            terms.append(param_value)

        if len(terms)==0:
            raise Exception("You didn't pass any URL parameters!")
        elif len(terms)==1:
            return jsonify(results=search_functions.get_autocomplete_skills(terms[0]),error=None)
        else:
            raise Exception("You passed in multiple URL params. If you want autocomplete for a multi word text, put all the words in one param separated with spaces.")

    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST

