from mongokit import Document
from project.services.database import Database
from project import utils
from project.config import config
from bson.objectid import ObjectId
from bson import uuid

Invites = Database['Invites']
connection = Database.connection()


@connection.register
class Invite(Document):
    __collection__ = 'Invites'
    __database__ = config['DATABASE_NAME']
    structure = {
        'producerObjectId': ObjectId,
        'consumerObjectId': ObjectId,
        'code': basestring,
        'scratchedOut': bool
    }

    default_values = {
        'scratchedOut': False
    }

    required_fields = ['code']

    basic_fields = {'_id', 'code', 'producerObjectId', 'consumerObjectId', 'scratchedOut'}

    use_dot_notation = True

    def __repr__(self):
        return '<Invite %r>' % str(self['producerObjectId'])


def create_invite(producer_object_id):
    invite = Invites.Invite()
    invite['producerObjectId'] = producer_object_id
    invite['code'] = str(uuid.uuid4().hex)[12:]
    invite.save()
    return invite


def get_invite_attributes(invite):
    return utils.jsonFields(invite, Invite.basic_fields, response=False)


def find_invite(map_attributes):
    return Invites.Invite.find_one(map_attributes)


def find_multiple_invites(map_attributes):
    return Invites.Invite.find(map_attributes)


def find_invite_by_code(invite_code):
    return find_invite({'code': invite_code})


def find_invite_by_id(invite_id):
    return find_invite({'_id': ObjectId(invite_id)})


def consume(invite_code, consumer_object_id):
    entry = find_invite_by_code(invite_code)
    if entry is None:
        raise Exception('Invalid code')
    if entry['consumerObjectId'] is not None:
        raise Exception('Code has already been consumed')
    entry['consumerObjectId'] = consumer_object_id
    entry.save()


def put_invite(invite_id, fields):
    entry = find_invite_by_id(invite_id)
    entry['scratchedOut'] = fields['scratchedOut']
    entry.save()


def is_valid(invite_code):
    invite = find_invite_by_code(invite_code)
    if invite is None:
        return False
    elif invite.consumerObjectId is not None:
        return False
    else:
        return True
