from project import es, DATABASE_NAME


#TODO: make this search query better, currently returns anything that matches any of the keywords
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
                "type":                 "most_fields",
                "fields":               ['_all'],
                "tie_breaker":          0.3,
                "minimum_should_match": "5%"
            }
        }
    }

    res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
    return res['hits']['hits']


def filtered_search_users(query_string, json_filter):
    """
    Takes a list of space separated words to query the database
    and a filter in json format. Returns a list of matching results.
    """

    query = {
    "query":
    {
    "filtered": {
        "query":  {  "multi_match": {
                "query":                query_string,
                "type":                 "most_fields",
                "fields":               ["_all"]
            }
                  },
        "filter": { "term":   json_filter }
        }
      }
    }
    print query
    res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
    return res['hits']['hits']