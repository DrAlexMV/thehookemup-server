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

    /api/v1/search?query_string=hardware%20java%20ibm&role=programmer&firstName=tanner&results_per_page=5&page_number=7

    will search for all users that have the words hardware, java, and ibm anywhere in their information,
    and it will then filter those results to only results that have the role set to "programmer" and the
    firstName set to "tanner". Setting the results_per_page and page_number behaves as you would expect it to.

    Results are returned in the form of a list of json results.

    """
    error = None
    list_filters = []
    try:
        query_string = request.args.get('query_string')
        results_per_page = request.args.get('results_per_page')
        page_number = request.args.get('page_number')
        
        keyed_queries = {}
        for constraint, value in request.args.items():
            if constraint == 'query_string' or constraint == 'results_per_page' or constraint == 'page_number':
                continue
            keyed_queries[constraint] = value.lower()

        if query_string is not None:
            query_string = query_string.lower()
        if results_per_page is not None:
            results_per_page = int(results_per_page)
        if page_number is not None:
            page_number = int(page_number)

        if keyed_queries:
            results = search_functions.filtered_search_users(query_string, [{'term':keyed_queries}], results_per_page, page_number)
        else:
            #call basic search
            results = search_functions.simple_search_users(query_string, results_per_page, page_number)

    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST

    ## now turn the queries into basic users
    user_ids = map(ObjectId, (entry['_id'] for entry in results.data))
    basic_users = user.get_basic_info_from_ids(user_ids)
    return jsonify(results=basic_users, metadata=results.metadata, error=None)



@search_blueprint.route(ROUTE_PREPEND+'/search/autocomplete/skills', methods=['GET'])
@login_required
def autocomplete_skill():
    """
    Example:

    GET http://localhost:5000/api/v1/search/autocomplete/skills?text=jav&results=2

    returns:

    {
        "error": null,
        "results": [{
            "score" : 10,
            "text" : "Java"
        },
            "score" : 2,
            "text" : "Javascript"
        }]
    }

    Where score is the number of users who have put that skill on their profile. Results are ordered by occurrence.
    In this case, both Java and Javascript match the text "jav" and java has 10 active users who list it as a skill
    and javascript has 2 active users who list it as a skill.

    """
    error = None

    try:
        num_results = request.args.get('results')
        text_to_search = request.args.get('text')

        return jsonify(results=search_functions.get_autocomplete_skills(text_to_search, num_results),error=None)

    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST


@search_blueprint.route(ROUTE_PREPEND+'/search/skills', methods=['GET'])
@login_required
def search_skills():
    """
    Example request:

    GET http://localhost:5000/api/v1/search/skills?text=couch&results=3

    Example response:

    {
        "error": null,
        "results": [{
            "name": "couch",
            "occurences": 4
        },
        {
            "name": "cooch",
            "occurences": 2
        },
        {
            "name": "couchs",
            "occurences": 1
        }]
    }

    To search for all skills, use

    GET http://localhost:5000/api/v1/search/skills?text=&results=<number of results wanted>

    """

    try:
        text_to_search = request.args.get('text')
        num_results = request.args.get('results')

        return jsonify(results=search_functions.simple_search_skills(text_to_search,num_results),error=None)

    except Exception as e:
        return jsonify(error=str(e)), HTTP_400_BAD_REQUEST

