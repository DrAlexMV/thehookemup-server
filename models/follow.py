from bson.objectid import ObjectId
from project import Follows
from mongokit import Document
from project import connection
from models.user import getUserID


@connection.register
class Follow(Document):
    __collection__ = 'Follows'
    __database__ = 'thehookemup'
    structure = {
        'followees': [{'_id': ObjectId, 'type': basestring}],
        'followers': [{'_id': ObjectId, 'type': basestring}],
        'entityType': basestring
    }

    required_fields = ['entityType']

coll = Follows


def get_or_create(entity_id, entity_type):
    entity_follows = coll.Follow.find_one({'_id': entity_id})
    if not entity_follows:
        entity_follows = coll.Follow()
        entity_follows['_id'] = entity_id
        entity_follows['entityType'] = entity_type
    return entity_follows


def add_or_pass(followers_follows, entity):
    if not filter(lambda e: e['_id'] == entity['_id'], followers_follows):
        followers_follows.append(entity)


def follow_entity(entity_id, entity_type):
    entity_id = ObjectId(entity_id)
    user_id = ObjectId(getUserID('me'))

    if entity_id == user_id:
        raise Exception('Cannot follow self')

    entity_follows = get_or_create(entity_id, entity_type)
    user_follows = get_or_create(user_id, 'user')

    add_or_pass(entity_follows['followers'], {'_id': user_id, 'type': 'user'})
    add_or_pass(user_follows['followees'], {'_id': entity_id, 'type': entity_type})

    entity_follows.save()
    user_follows.save()
    return entity_follows


def inject_entity(action):
    def inject(*args, **kwargs):
        entity_id = getUserID('me') if kwargs['entity_id'] == 'me' else kwargs['entity_id']
        entity = coll.Follow.find_one({'_id': ObjectId(entity_id)})
        return action(entity)
    return inject


@inject_entity
def count(entity):
    followee_count = len(entity['followees']) if entity else 0
    follower_count = len(entity['followers']) if entity else 0
    return {'followees': followee_count, 'followers': follower_count}


@inject_entity
def followers(entity):
    return entity['followers'] if entity else None


@inject_entity
def followees(entity):
    return entity['followees'] if entity else None








