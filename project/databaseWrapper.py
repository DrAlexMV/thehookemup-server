from project import es, DATABASE_NAME
from bson.json_util import dumps


def save_entity(entity):
        entity.save()
        obj_id = str(entity._id)
        #delete the entity from elastic search if it already exists
        es.delete(index=DATABASE_NAME,doc_type=type(entity).__name__, id=obj_id, ignore=[400, 404])
        #resave the entity into elastic search
        es.index(index=DATABASE_NAME, doc_type=type(entity).__name__, id=obj_id, body=dumps(entity))
        print "made it here!"

#TODO: make this search query better, currently returns anything that matches any of the keywords
def search_database_users(keywords):

        querystring = ""
        for key in keywords:
            querystring+=key+" "
        query={
               "query":{
                   "multi_match": {
                   "query":                querystring,
                   "type":                 "best_fields",
                   "fields":               ["firstName", "lastName", "role"],
                   "tie_breaker":          0.3,
                   "minimum_should_match": "1%"
                }
             }
        }

        res = es.search(index=DATABASE_NAME, doc_type='User', body=query)
        return res
        #return res['hits']['hits']
