from project.services.elastic import Elastic
import requests
import json
from project.config import config

es = Elastic.connection()

#TODO: Some things that should be done to make these searches better is to weight
#TODO: unique words more highly. This is an option in elastic search, and it shouldn't
#TODO: be difficult to implement.

#TODO: Put all these arbitrary parameters in a search config file


class SearchResults:
    def __init__(self, data, metadata):
        self.data = data
        self.metadata = metadata


def simple_search_users(query_string, results_per_page, page):
    """
    Takes a string of space separated words to query, returns a list
    of user entities that have those keywords in any fields.
    This is to be used when filter params are not specified.
    """
    if not query_string:
        query = {
            "query": {
                "match_all": {}
            }
        }
    else:
        query = {
                "query":{
                    "multi_match": { #match against multiple fields
                    "query":                query_string, #string that was entered in. automatically parsed into words
                    "fuzziness": 3,  #Levenshtein Edit Distance
                    "type":                 "most_fields", #combine the score of all matching fields
                    "fields":               ['_all', "skills^3"], #match against all indexed fields, boost the value of matches with skills
                    "minimum_should_match": "5%" #at least 5% of the words in query_string should match
                }
            }
        }
    if page == None or results_per_page == None:
        res = es.search(index=config['DATABASE_NAME'], doc_type='User', body=query)['hits']['hits']
    else:
        res = es.search(index=config['DATABASE_NAME'], doc_type='User', body=query, from_=page*results_per_page, size=results_per_page)['hits']['hits']
    number_results = es.count(index=config['DATABASE_NAME'], doc_type='User', body=query)['count']
    return SearchResults(res,{'numberResults': number_results})


def filtered_search_users(query_string, json_filter_list, results_per_page, page):
    """
    Takes a list of space separated words to query the database
    and a list of filter in json format, i.e. [{term:filter}].
    Returns a list of json results ordered by degree of matching.
    """

    #if the query string is blank, just search based on the filters
    #currently unused since we don't support empty string queries

    if not query_string:

        query = {
            "query":{
                "filtered": {
                    "query":  {
                        "match_all":{}
                    },
                    "filter": {
                        "bool":{
                            "must":json_filter_list
                        }
                    }
                }
            }
        }
    else:
        query = {
            "query":{
                "filtered": {
                    "query":  {
                        "multi_match": {
                            "query":               query_string,
                            "fuzziness": 3,
                            "type":                 "most_fields",
                            "fields":               ["_all"]
                        }
                    },
                    "filter": {
                        "bool":{
                            "must":json_filter_list
                        }
                    }
                }
            }
        }

    #print query
    if page == None or results_per_page == None:
        res = es.search(index=config['DATABASE_NAME'], doc_type='User', body=query)['hits']['hits']
    else:
        res = es.search(index=config['DATABASE_NAME'], doc_type='User', body=query, from_=page*results_per_page, size=results_per_page)['hits']['hits']
    number_results = es.count(index=config['DATABASE_NAME'], doc_type='User', body=query)['count']
    return SearchResults(res, {'number_results': number_results})

def get_autocomplete_skills(text, num_results):
    query = {
    "skills" : {
        "text" : text,
        "completion" : {
            "field" : "name_suggest",
            "size": num_results
            }
        }
    }
    headers = {'content-type': 'application/json'}
    url =  url = 'http://'+config['ELASTIC_HOST']+":"+str(config['ELASTIC_PORT'])+'/' + config['DATABASE_NAME']+ '-skills/_suggest'
    res = requests.post(url, data=json.dumps(query), headers=headers)
    return res.json()['skills'][0]['options']


def get_autocomplete_markets(text, num_results):
    query = {
    "markets" : {
        "text" : text,
        "completion" : {
            "field" : "name_suggest",
            "size": num_results
            }
        }
    }
    headers = {'content-type': 'application/json'}
    url =  url = 'http://'+config['ELASTIC_HOST']+":"+str(config['ELASTIC_PORT'])+'/' + config['DATABASE_NAME']+ '-markets/_suggest'
    res = requests.post(url, data=json.dumps(query), headers=headers)
    return res.json()['markets'][0]['options']

def simple_search_skills(text, num_results):

    if not text:
        query = {
            "sort" : [{
                "occurrences": {
                    "order": "desc"
                }
            }],
            "query": {
                "match_all": {}
            }
        }
    else:
        query = {
            "sort" : [{
                "occurrences" : {
                    "order" : "desc"
                }
            }],
           "query":  {
                "multi_match": {
                    "query":               text,
                    "fuzziness":    4,
                    "fields":       ["name"]
                }
            }
        }

    headers = {'content-type': 'application/json'}
    url = 'http://'+config['ELASTIC_HOST']+":"+str(config['ELASTIC_PORT'])+'/' + config['DATABASE_NAME']+ '-skills/_search?size='+str(num_results)
    res = requests.post(url, data=json.dumps(query), headers=headers)
    unfiltered_results = res.json()['hits']['hits']
    filtered_results = map(lambda result: {"name":result["_source"]["name"], "occurrences":result["_source"]["occurrences"]}, unfiltered_results)
    return filtered_results