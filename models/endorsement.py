from bson.objectid import ObjectId
from project import Endorsements
from mongokit import Document
from project import connection
from models.user import getUserID, findUserByID, get_basic_info_with_security, get_basic_info_from_ids
from models.startup import find_startup_by_id, get_basic_startup, get_basic_startups_from_ids
from itertools import groupby
from mongokit.paginator import Paginator



@connection.register
class Endorsement(Document):
    __collection__ = 'Endorsements'
    __database__ = 'thehookemup'
    structure = {
        'endorsees': [{'_id': ObjectId, 'entityType': basestring}],
        'endorsers': [{'_id': ObjectId, 'entityType': basestring}],
        'entityType': basestring
    }

    required_fields = ['entityType']

coll = Endorsements


def find_entity_by_type(entity_id, entity_type):
    find = find_startup_by_id if entity_type == 'startup' else findUserByID
    return find(entity_id)


def find_entities_basic_info_by_type(entity_ids, entity_type):
    print entity_ids, entity_type
    basic_info = get_basic_startups_from_ids if entity_type == 'startup' else get_basic_info_from_ids
    return basic_info(entity_ids)


def find_entity_basic_info_by_type(entity_id, entity_type):
    basic_info = get_basic_startup if entity_type == 'startup' else get_basic_info_with_security
    return basic_info(find_entity_by_type(entity_id, entity_type))


def find_entity_list_by_type(entity_list):
    if entity_list:
        grouped = groupby(entity_list, key=lambda e: e['entityType'])
        return reduce(lambda acc, (entity_type, entities):
                      acc + find_entities_basic_info_by_type([ e['_id'] for e in entities ], entity_type), grouped, [])
    return []


def find_endorsements_by_id(entity_id):
    entity_id = getUserID(entity_id) if entity_id == 'me' else entity_id
    return coll.Endorsement.find_one({'_id': ObjectId(entity_id)})


def inject_entities(action):
    def inject(*args, **kwargs):
        entities = [find_endorsements_by_id(entity_id) for entity_id in args]
        return action(*entities)
    return inject


def inject_entity(action):
    def inject(*args, **kwargs):
        entity_id = kwargs['entity_id']
        if not entity_id:
            raise Exception('An entity id must be provided')
        return action(find_endorsements_by_id(entity_id), *args)
    return inject


def get_or_create(entity_id, entity_type):
    entity_id = getUserID(entity_id) if entity_id == 'me' else entity_id
    entity_endorsements = coll.Endorsement.find_one({'_id': entity_id})
    if not entity_endorsements:
        if find_entity_by_type(entity_id, entity_type):
            entity_endorsements = coll.Endorsement()
            entity_endorsements['_id'] = entity_id
            entity_endorsements['entityType'] = entity_type
        else:
            raise Exception('%s does not exist' % entity_type)
    return entity_endorsements


def add_or_pass(endorser_endorsements, entity):
    if not filter(lambda e: e['_id'] == entity['_id'], endorser_endorsements):
        endorser_endorsements.append(entity)


def endorse_entity(entity_id, entity_type):
    entity_id = ObjectId(entity_id)
    user_id = ObjectId(getUserID('me'))

    if entity_id == user_id:
        raise Exception('Cannot endorse self')

    entity_endorsements = get_or_create(entity_id, entity_type)
    user_endorsements = get_or_create(user_id, 'user')

    add_or_pass(entity_endorsements['endorsers'], {'_id': user_id, 'entityType': 'user'})
    add_or_pass(user_endorsements['endorsees'], {'_id': entity_id, 'entityType': entity_type})

    entity_endorsements.save()
    user_endorsements.save()
    return user_endorsements['endorsees']


@inject_entity
def count(entity):
    endorsee_count = len(entity['endorsees']) if entity else 0
    endorser_count = len(entity['endorsers']) if entity else 0
    return {'endorsees': endorsee_count, 'endorsers': endorser_count}


@inject_entity
def endorsers(entity):
    return entity['endorsers'] if entity else None


@inject_entity
def endorsees(entity):
    return entity['endorsees'] if entity else None


@inject_entities
def remove_endorsement(endorser, endorsee):
    def find_remove(entity, to_remove, role):
        entity[role] = filter(lambda e: e['_id'] != to_remove['_id'], entity[role])
        entity.save()

    find_remove(endorsee, endorser, 'endorsers')
    find_remove(endorser, endorsee, 'endorsees')

    return endorser


def user_remove_endorsement(entity_id):
    return remove_endorsement('me', entity_id)


def populate_counts(users):
    for user in users:
        user['endorsementCount'] = count(entity_id=user['_id'])


@inject_entity
def has_entity_endorsed(endorser, endorsee_id):
    endorsee_id = ObjectId(endorsee_id)
    found = filter(lambda e: e['_id'] == endorsee_id, endorser['endorsees'])
    return bool(found)


def get_entities_by_num_endorsements(entity_type, page, results_per_page):
     endorsements = Endorsements.Endorsement.find( sort = [('endorsers', -1)])
     paged_endorsements = Paginator(endorsements, page, results_per_page)
     endorsements = paged_endorsements.items
     ranked_entities = [{'_id':endorsement['_id'], 'entityType':endorsement['entityType']} for endorsement in endorsements]
     startups = filter(lambda e: e['entityType'] == entity_type, ranked_entities)
     return map(lambda e:find_entity_basic_info_by_type(e['_id'], entity_type), startups)











