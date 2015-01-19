from project import es, DATABASE_NAME
import requests
import json
from project.config import config

#TODO: Some things that should be done to make these searches better is to weight
#TODO: unique words more highly. This is an option in elastic search, and it shouldn't
#TODO: be difficult to implement.

#TODO: Put all these arbitrary parameters in a search config file

def simple_search_users(query_string):
    """
    Takes a string of space separated words to query, returns a list
    of user entities that have those keywords in any fields.
    This is to be used when filter params are not specified.
    """

    if query_string=='' or query_string==None:
        query= {
            "query" : {
                "match_all" : {}
            }
        }
    else:
        query={
                "query":{
                    "multi_match": {
                    "query":                query_string,
                    "fuzziness": 4,
                    "type":                 "most_fields",
                    "fields":               ['_all'],
                    "tie_breaker":          0.3,
                    "minimum_should_match": "5%"
                }
            }
        }

    res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
    return res['hits']['hits']


def filtered_search_users(query_string, json_filter_list):
    """
    Takes a list of space separated words to query the database
    and a list of filter in json format, i.e. [{term:filter}].
    Returns a list of json results ordered by degree of matching.
    """

    #if the query string is blank, just search based on the filters
    #currently unused since we don't support empty string queries
    if query_string == '' or query_string==None:
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
                            "fuzziness": 4,
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
    res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
    return res['hits']['hits']


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
    res = requests.post("http://localhost:9200/skills/_suggest", data=json.dumps(query), headers=headers)
    return res.json()['skills'][0]['options']

def simple_search_skills(text, num_results):

    if text=='' or text==None:
        query = {
            "sort" : [{
                "occurrences" : {
                    "order" : "desc"
                }
            }],
            "query" : {
                "match_all" : {}
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
    url = "http://"+config['ELASTIC_HOST']+":"+str(config['ELASTIC_PORT'])+"/skills/_search?size="+str(num_results)
    res = requests.post(url, data=json.dumps(query), headers=headers)
    unfiltered_results = res.json()['hits']['hits']
    filtered_results = map(lambda result: {"name":result["_source"]["name"], "occurrences":result["_source"]["occurrences"]}, unfiltered_results)
    return filtered_results

