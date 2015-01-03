from flask import request, Blueprint, jsonify
from flask.ext.login import login_required
from project import ROUTE_PREPEND, utils
from flask.ext.api.status import *
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

    /api/v1/search?query_string='hardware java ibm'&arg1={"role":"programmer"}&arg2={"firstName":"tanner"}

    will search for all users that have the words hardware, java, and ibm anywhere in their information,
    and it will then filter those results to only results that have the role set to "programmer" and the
    firstName set to "tanner". Results are returned in the form of a list of json results.

    """
    error = None
    list_filters = []
    try:
        query_string = request.args.get('query_string')
        arg_index = 0
        for constraint in request.args:
            if constraint=='query_string':
                continue
            next_term_filter = request.args[constraint]
            next_term_filter_list = utils.fix_term_filter(ast.literal_eval(next_term_filter))
            list_filters=list_filters+next_term_filter_list
        if query_string!=None:
            query_string=query_string.lower()
        if list_filters == []:
            #call basic search
            results = search_functions.simple_search_users(query_string)
        else:
            filter_json_list = []
            for filter in list_filters:
                filter_json_list.append({'term':filter})
            results = search_functions.filtered_search_users(query_string,filter_json_list)
    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
    return jsonify(results=results, error=None)