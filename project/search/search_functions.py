from project import es, DATABASE_NAME


#TODO: Some things that should be done to make these searches better is to weight
#TODO: unique words more highly. This is an option in elastic search, and it shouldn't
#TODO: be difficult to implement.

def simple_search_users(query_string):
    """
    Takes a string of space separated words to query, returns a list
    of user entities that have those keywords in any fields.
    This is to be used when filter params are not specified.
    """
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