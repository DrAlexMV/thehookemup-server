from mongokit import *
from project import Invites
from project import connection
from project import database_wrapper
from project import utils
from bson.objectid import ObjectId
from bson import uuid

@connection.register
class Invite(Document):
    __collection__ = 'Invites'
    __database__ = 'thehookemup'
    structure = {
        'producerObjectId': basestring,
        'consumerObjectId': basestring,
        'code': basestring,
        'scratchedOut': bool
    }
    
    default_values = {
        'scratchedOut': False
    }

    required_fields = ['producerObjectId', 'code']

    basic_fields = {'_id', 'code', 'producerObjectId', 'consumerObjectId', 'scratchedOut'}

    use_dot_notation = True
    def __repr__(self):
        return '<Invite %r>' % (self.producerObjectId)

def create_invite(producer_object_id):
    #takes an object_id
    producer_object_id=str(producer_object_id)
    invite = Invites.Invite()
    invite['producerObjectId'] = producer_object_id
    invite['code'] = str(uuid.uuid4().hex)[12:]
    invite.save()
    return invite

def get_invite_attributes(invite):
    return utils.jsonFields(invite, Invite.basic_fields, response=False)

def find_invite(map_attributes):
    return Invites.Invite.find_one(map_attributes)

def find_multiple_invites(mapAttributes):
    return Invites.Invite.find(mapAttributes)

def find_invite_by_code(invite_code):
    return find_invite({'code': invite_code})

def find_invite_by_id(invite_id):
    return find_invite({'_id': ObjectId(invite_id)})

def consume_invite(invite_code, consumer_object_id):
    entry = find_invite_by_code(invite_code)
    if entry['consumerObjectId'] != None:
        raise Exception("Code has already been consumed")
    entry['consumerObjectId'] = consumer_object_id
    entry.save()

def put_invite(invite_id, fields):
    entry = find_invite_by_id(invite_id)
    entry['scratchedOut'] = fields['scratchedOut']
    entry.save()
