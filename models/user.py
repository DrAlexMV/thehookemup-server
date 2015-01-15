from mongokit import *
from project import bcrypt
import datetime
from project import connection
from project import Users
from project import utils
from project import database_wrapper
from bson.objectid import ObjectId
from flask.ext.login import current_user
from flask.ext.api.status import HTTP_401_UNAUTHORIZED

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
            'connections': [{'user': basestring, 'type': basestring}],
            'associations': [basestring]
        }

    }
    required_fields = ['firstName', 'lastName', 'email', 'password', 'role']
    
    connection_types = {'CONNECTED': 'c', 'PENDING_APPROVAL': 'pa', 'SENT': 's'}
    acceptable_details = {'skills', 'interests', 'projects'}

    basic_info_fields = {
        'firstName',
        'lastName',
        'dateJoined',
        'role',
        'graduationYear',
        'major',
        'university',
        'description',
        'picture',
        '_id'
    }

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

    ## give em all the possible details
    user.details = [{'content':[], 'title': det_title} for det_title in User.acceptable_details]

    return user

def addJob(user, jsonAttributes):
    user['jobs'].append(jsonAttributes)

def update_details(user, request_details, patch = False):
    current_detail_titles = {detail['title'] for detail in user['details']}
    for request_detail in request_details:
        if (not patch) and (not request_detail['title'] in User.acceptable_details):
            raise Exception('Illegal detail: %s'%request_detail['title'])

        if request_detail['title'] in current_detail_titles: # O(1)
            if not patch:
                raise Exception("You tried to PUT a detail which has the same title as an existing detail. Titles for details are forced to be unique. To change an existing detail, use PATCH instead of PUT.")
        elif patch:
            raise Exception("You tried to PATCH a detail with a title that does not exist. To add a new detail, use PUT.")

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

        if patch:
            # insert into correct index
            for detail_idx, user_detail in enumerate(user.details):
                if request_detail['title'] == user_detail['title']:
                    user.details[detail_idx] = detail
                    break
        else:
            # add to end
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

def get_connections(this_user):
    connected = User.connection_types['CONNECTED']
    return [conn['user'] for conn in this_user['edges']['connections'] if conn['type'] == connected]

def get_pending_connections(this_user):
    pending = User.connection_types['PENDING_APPROVAL']
    return [conn['user'] for conn in this_user['edges']['connections'] if conn['type'] == pending]

## TODO: Adapt to make less silly. Right now it basically just gets 5 people not in your edges.connections
## Notes: this returns objects rather than ids
def get_suggested_connections(this_user):
    # do this in two steps since I'm not a Mongo Master
    user_ids = [ObjectId(conn['user']) for conn in this_user.edges.connections]
    user_ids.append(this_user._id)
    query = {'_id': {'$nin': user_ids}, 'firstName': {'$exists': True }}
    non_connections = Users.User.find(query, sort = [('picture', -1)], limit = 5)
    return non_connections

def get_connection(this_user, other_user_id):
    other_user_id = str(other_user_id)
    for conn in this_user['edges']['connections']:
        if conn['user'] == other_user_id:
            return conn
    return None

def connection_type(other_user):
    me = findUserByID('me')
    other_user_id = str(other_user._id)
    if other_user_id == str(me._id):
        return 'c'

    our_connection = get_connection(me, other_user_id)

    if our_connection:
        return our_connection['type']
    else:
        return ''

def request_connection(other_user):
    conn_type = connection_type(other_user)
    me = findUserByID('me')

    if conn_type:
        raise Exception('user already added')

    sent_request = {'user': str(other_user._id), 'type': User.connection_types['SENT']}
    pending_approval_request = {'user': str(me._id), 'type': User.connection_types['PENDING_APPROVAL']}
    # add to me
    me['edges']['connections'].append(sent_request)

    # add to other
    other_user['edges']['connections'].append(pending_approval_request)

    ## only complete transaction after successful addition to both sides
    database_wrapper.save_entity(me)
    database_wrapper.save_entity(other_user)

def confirm_connection(other_user):
    conn_type = connection_type(other_user)
    me = findUserByID('me')

    if conn_type != 'pa':
        raise Exception('user not pending approval')

    get_connection(me, other_user._id)['type'] = User.connection_types['CONNECTED']
    get_connection(other_user, me._id)['type'] = User.connection_types['CONNECTED']

    ## only complete transaction after successful addition to both sides
    database_wrapper.save_entity(me)
    database_wrapper.save_entity(other_user)

def remove_connection(this_user, other_user_id):
    index = None

    for i, conn in enumerate(this_user['edges']['connections']):
        if conn['user'] == other_user_id:
            index = i
            break
    else:
        return False
    
    this_user['edges']['connections'].pop(index)
    return True

def remove_user_connection(other_user):
    me = findUserByID('me')

    our_connection = get_connection(me, other_user._id)

    if our_connection is None:
        raise Exception('no connection between you and this user')

    current_user_id = str(me._id)
    other_user_id = str(other_user._id)

    status_me = remove_connection(me, other_user_id)
    status_other = remove_connection(other_user, current_user_id)

    if not status_me or not status_other:
        raise Exception('removal failed due to missing links. database likely corrupt')

    ## only complete transaction after successful removal from both sides
    database_wrapper.save_entity(me)
    database_wrapper.save_entity(other_user)

# either confirms or requests depending on state of issuer
def handle_connection(other_user):
    conn_type = connection_type(other_user)
    if conn_type == User.connection_types['PENDING_APPROVAL']:
        confirm_connection(other_user)
    elif conn_type == '':
        request_connection(other_user)
    else:
        raise Exception('invalid action on this user')

def get_basic_info_with_security(userObject): # O(N)
    fields = list(User.basic_info_fields)
    conn_type = connection_type(userObject)
    if conn_type == User.connection_types['CONNECTED']:
        fields.append('email')

    return utils.jsonFields(userObject, fields, response = True, extra = { 'connectionType' : conn_type })

def get_basic_info_from_users(users):
    basic_users = []
    for user_object in users:
        basicuser = utils.jsonFields(user_object, User.basic_info_fields, response=False)
        basic_users.append(basicuser)
    return basic_users

# returns a list of json basic users from a list of user ids
def get_basic_info_from_ids(user_ids):
    queried = findMultipleUsers({'_id': {'$in': user_ids}})
    return get_basic_info_from_users(queried)

# decorator that protects other users from PUT/POST/DELETE on you stuff
# user_id _must_ be passed in as 'user_id'
def only_me(function):
    def inner(*args, **kwargs):
        if kwargs['user_id'] != 'me':
            return '{}', HTTP_401_UNAUTHORIZED
        return function(*args, **kwargs)
    return inner
