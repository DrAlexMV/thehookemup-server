from mongokit import *
from project import bcrypt
import datetime
from project import connection
from project import Users
from project import utils
from project import database_wrapper
from bson.objectid import ObjectId
from flask.ext.login import current_user

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

@connection.register
class User(Document):
    __collection__ = 'Users'
    __database__ = 'thehookemup'
    structure = {
        'firstName': basestring,
        'lastName': basestring,
        'email': basestring,
        'password': basestring,
        'dateJoined': datetime.datetime,
        'graduationYear': int,
        'major': basestring,
        'description': basestring,
        'university': basestring,
        'role': basestring,
        'picture': basestring,
        'details': [{
            'title': basestring,
            'content': [{
                'title': basestring,
                'description': basestring,
                'subpoints': [{
                    'title': basestring,
                    'description': basestring
                    }]
            }]
        }],
        'jobs':[{
                'companyName': basestring,
                'startDate': basestring,
                'endDate':  basestring,
                'description': basestring,
                'currentlyWorking': bool
                }],
        'edges': {
            'connections': [basestring],
            'associations': [basestring]
        }

    }
    required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
    
    basic_info_fields = set([
        'firstName',
        'lastName',
        'email',
        'dateJoined',
        'role',
        'graduationYear',
        'major',
        'university',
        'description',
        'picture',
        '_id'
    ])

    default_values = {
        'dateJoined': datetime.datetime.utcnow
    }
    validators = {
        'firstName': max_length(50),
        'lastName': max_length(50),
        'email': max_length(120),
        'password': max_length(120)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.firstName)

    #### Required to be implemented for login manager ####

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    #TODO: probably should use _id instead of email for login manager
    def get_id(self):
        return unicode(self.email)

    ######################################################

def createUser(jsonAttributes):
    user = Users.User()
    jsonAttributes['password'] = bcrypt.generate_password_hash(jsonAttributes['password'])

    utils.mergeFrom(jsonAttributes, user, User.required_fields)

    optional = User.basic_info_fields.difference(User.required_fields)
    optional.remove('_id')
    utils.mergeFrom(jsonAttributes, user, optional, require=False)

    return user

def addJob(user, jsonAttributes):
    user['jobs'].append(jsonAttributes)


def addDetail(user, request_detail):

    i=0
    for detail in user['details']:
        if detail['title']==request_detail['title']:
            user['details'].pop(i)
        i = i+1

    detail = {}
    detail['content']=[]
    detail['title']=request_detail['title']
    for request_content in request_detail['content']:
        content = {}
        content['subpoints']=[]
        content['title']=request_content['title']
        content['description']=request_content['description']
        for request_subpoint in request_content['subpoints']:
            subpoint = {}
            subpoint['title']=request_subpoint['title']
            subpoint['description']=request_subpoint['description']
            content['subpoints'].append(subpoint)
        detail['content'].append(content)
    user.details.append(detail)

    database_wrapper.save_entity(user)

def removeDetail(user, detail_title):
    i = 0
    for detail in user['details']:
        if detail['title'] == detail_title:
            user['details'].pop(i)
            database_wrapper.save_entity(user)
            return True
        i=i+1
    return False

def add_connection(user, connection):
    user_id = str(user['_id'])
    connection_id = str(connection['_id'])

    if connection_id in user['edges']['connections']:
        raise Exception('user already added')

    user['edges']['connections'].append(connection_id)
    connection['edges']['connections'].append(user_id)

    ## only complete transaction after successful addition to both sides
    database_wrapper.save_entity(user)
    database_wrapper.save_entity(connection)

def remove_connection(user, connection):
    connection_id = str(connection['_id'])

    user['edges']['connections'].remove(str(connection['_id']))
    connection['edges']['connections'].remove(str(user['_id']))

    ## only complete transaction after successful removal from both sides
    database_wrapper.save_entity(user)
    database_wrapper.save_entity(connection)

## Normalizes userid to ObjectId
def getUserID(userid):
    if userid == 'me':
        return current_user._id
    try:
        return ObjectId(userid)
    except:
        pass

## Like FindSingleUser but takes a string.
def findUserByID(userid):
    uid = getUserID(userid)
    entry = Users.User.find_one({'_id': uid})
    return entry

def findSingleUser(mapAttributes):
    entry = Users.User.find_one(mapAttributes)
    return entry

def findMultipleUsers(mapAttributes):
    entries = Users.User.find(mapAttributes)
    return entries

# returns a list of json basic users from a list of user ids
def get_basic_info_from_ids(user_ids):
    basic_users = []
    queried = findMultipleUsers({'_id': {'$in': user_ids}})
    for connection_userid in queried:
        basicuser = utils.jsonFields(connection_userid, User.basic_info_fields, response=False)
        basic_users.append(basicuser)
    return basic_users
