from mongokit import *
from project import Invites
from project import connection
from project import database_wrapper
from bson.objectid import ObjectId


@connection.register
class Invite(Document):
    __collection__ = 'Invites'
    __database__ = 'thehookemup'
    structure = {
        'producerObjectId': basestring,
        'consumerObjectId': basestring,
        'scratchedOut': bool
    }
    
    default_values = {
        'scratchedOut': False
    }

    required_fields = ['producerObjectId']

    use_dot_notation = True
    def __repr__(self):
        return '<Invite %r>' % (self.producerObjectId)

def create_invite(producer_object_id):
    #takes an object_id
    producer_object_id=str(producer_object_id)
    invite = Invites.Invite()
    invite['producerObjectId'] = producer_object_id
    invite.save()
    return invite

def get_invite_attributes(invite):
    output={}
    output['inviteCode']=str(invite._id)
    output['producerObjectId']=invite['producerObjectId']
    output['consumerObjectId']=invite['consumerObjectId']
    output['scratchedOut']=invite['scratchedOut']
    return output


def find_invite_by_id(invite_id):
    #takes a string id
    entry = Invites.Invite.find_one({'_id': ObjectId(invite_id)})
    return entry


def find_invite(map_attributes):
    entry = Invites.Invite.find_one(map_attributes)
    return entry


def find_multiple_invites(mapAttributes):
    entries = Invites.Invite.find(mapAttributes)
    return entries


def consume_invite(invite_id, consumer_object_id):
    entry = Invites.Invite.find_one({'_id': ObjectId(invite_id)})
    if entry['consumerObjectId']!=None:
        raise Exception("Code has already been consumed")
    entry['consumerObjectId'] = consumer_object_id
    entry.save()

def put_invite(invite_id, fields):
    entry = Invites.Invite.find_one({'_id': ObjectId(invite_id)})
    entry['scratchedOut'] = fields['scratchedOut']
    entry.save()
