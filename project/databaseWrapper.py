from project import es, DATABASE_NAME
from models import user, image
from bson.json_util import dumps
import sys

def save_entity(entity):
    try:
        entity.save()
        obj_id = str(entity._id)
        #delete the entity from elastic search if it already exists
        es.delete(index=DATABASE_NAME,doc_type=type(entity).__name__, id=obj_id, ignore=[400, 404])
        #resave the entity into elastic search
        es.index(index=DATABASE_NAME, doc_type=type(entity).__name__, id=obj_id, body=dumps(entity))
    except:
         e = sys.exc_info()[0]
         return "Error saving to database or elasticsearch: " + str(e)
    return "Saved properly"

#TODO: make this search query better, currently returns anything that matches any of the keywords
def search_database_users(keywords):
        #type to search is the string name of the doc_type, e.g. User or Image
        querystring = ""
        for key in keywords:
            querystring+=key+" "
        query={
               "query":{
                   "multi_match": {
                   "query":                querystring,
                   "type":                 "best_fields",
                   "fields":               ["first_name", "last_name", "description"],
                   "tie_breaker":          0.3,
                   "minimum_should_match": "1%"
                }
             }
        }

        res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
        return res['hits']['hits']
