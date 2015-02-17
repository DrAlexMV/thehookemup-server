from flask_mongokit import Document
from project.services.auth import Auth
import copy


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate


class BaseUser(Document):

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        self.collection.ensure_index([('email', 1)], unique=True)

    structure = {
        "firstName": unicode,
        "lastName": unicode,
        "email": unicode,
        "password": basestring,
        "permissionLevel": int
    }

    validators = {
        "firstName": max_length(50),
        "lastName": max_length(50),
        "email": max_length(120),
        "password": max_length(120)
    }

    required_fields = ["firstName", "lastName", "email", "password", "permissionLevel"]

    basic_info_fields = {
        "_id",
        "firstName",
        "lastName",
        "permissionLevel"
    }

    def to_basic(self):
        return {k: self[k] for k in self.basic_info_fields}

    def get_access_level(self):
        return self["permissionLevel"]

    def is_active(self):
        return self["permissionLevel"] > Auth.GHOST

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self['_id'])


def prepare(attributes):
    attributes_copy = copy.deepcopy(attributes)
    attributes_copy['password'] = Auth.hash_password(attributes['password'])
    attributes_copy['email'] = attributes['email'].lower()
    attributes_copy['permissionLevel'] = Auth.GHOST
    return attributes_copy

