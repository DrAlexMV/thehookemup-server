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
        'consumerObjectId': basestring
        }
    
    required_fields = ['producerObjectId']

    '''default_values = {
        'occurrences': 1
    }'''

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


def consumeInvite(invite_id, consumer_object_id):
    entry = Invites.Invite.find_one({'_id': ObjectId(invite_id)})
    if entry['consumerObjectId']!=None:
        raise Exception("Code has already been consumed")
    entry['consumerObjectId'] = consumer_object_id
    entry.save()


#TODO: delete invites from elastic and database if decremented to zero
def decrement_invite(invite):
    if invite.occurrences == 1:
       database_wrapper.remove_entity(invite)
    else:
        invite.occurrences -= 1
        database_wrapper.save_entity(invite)