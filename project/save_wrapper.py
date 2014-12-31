from project import es, DATABASE_NAME
from models import user, image
from bson.json_util import dumps

def save_entity(entity):
    entity.save()
    es.index(index=DATABASE_NAME, doc_type=type(entity).__name__, id=str(entity._id), body=dumps(entity))


