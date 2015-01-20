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
from flask import jsonify
import skill

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
        'roles': [basestring],
        'picture': basestring,
        'interests': [{
            'title': basestring,
            'description': basestring,
        }],
        'projects':[{
            'date': basestring,
            'title': basestring,
            'description': basestring,
            'details': [{
                'title': basestring,
                'description': basestring
                        }],
            'people':[basestring]
        }],
        'skills':[basestring], #tags
        'edges': {
            'connections': [{'user': basestring, 'type': basestring, 'message': basestring,
                             'date': datetime.datetime}],  # date when request was sent
            'associations': [basestring]
        }

    }
    required_fields = ['firstName', 'lastName', 'email', 'password', 'roles']
    
    connection_types = {'CONNECTED': 'c', 'PENDING_APPROVAL': 'pa', 'SENT': 's'}

    basic_info_fields = {
        'firstName',
        'lastName',
        'dateJoined',
        'roles',
        'graduationYear',
        'major',
        'university',
        'description',
        'picture',
        '_id'
    }

    details = {
        'interests',
        'projects',
        'skills'
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
    jsonAttributes['email']=jsonAttributes['email'].lower()
    utils.mergeFrom(jsonAttributes, user, User.required_fields)
    optional = User.basic_info_fields.difference(User.required_fields)
    optional.remove('_id')
    utils.mergeFrom(jsonAttributes, user, optional, require=False)

    return user

def get_skills_from_name(list_of_skill_name):
    output = []
    for name in list_of_skill_name:
        found_skill = skill.find_skill({"name":name})
        if found_skill == None:
            #need to create a new skill
            output.append(skill.create_skill(name, 0))
        else:
            output.append(found_skill)
    return output

def get_skills_from_id(list_of_skill_id):
    output = []
    for id in list_of_skill_id:
        output.append(skill.find_skill_by_id(id))
    return output


#TODO: clean this shit up
def put_skills(user,req):
    skills = req.get('skills')
    previous_skills_list = get_skills_from_id(user['skills'])
    put_skills_list = get_skills_from_name(skills)
    removed_skills = utils.arr_diff(previous_skills_list,put_skills_list)
    added_skills = utils.arr_diff(put_skills_list,previous_skills_list)

    for removed_skill in removed_skills:
        if removed_skill == None:
            #this should never happen
            raise Exception("User had reference to skill that doesn't exist")
        else:
            skill.decrement_skill(removed_skill)

    for added_skill in added_skills:
        if added_skill == None:
            #this should never happen
            raise Exception("Something broke.. Added skill is None?!")
        else:
            skill.increment_skill(added_skill)

    user.skills = [str(put_skill._id) for put_skill in put_skills_list]
    database_wrapper.save_entity(user)
    return True

def put_interests(user, req):
    interests = req.get('interests')
    user.interests = interests
    database_wrapper.save_entity(user)
    return True

def put_projects(user, req):
    projects = req.get('projects')
    user.projects = projects
    database_wrapper.save_entity(user)
    return True

#TODO: clean this up, use the details field defined above
def get_user_details(user):
    output = {}
    output['interests']=user['interests']
    output['skills']=[]
    for skill_id in user['skills']:
        output['skills'].append(skill.find_skill_by_id(skill_id)['name'])
    output['projects'] = []

    # annotate with full basic info
    for project in user['projects']:
        p = project.copy()
        ids =  map(ObjectId, p['people'])
        p['people'] = get_basic_info_from_ids(ids)
        output['projects'].append(p)

    return jsonify(output)
    '''fields = list(User.details)
    conn_type = connection_type(user)
    return utils.jsonFields(user, fields, response = True, extra = { 'connectionType' : conn_type })'''



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

#
def findMultipleUsers(mapAttributes):
    entries = Users.User.find(mapAttributes)
    return entries

def get_connections(this_user):
    connected = User.connection_types['CONNECTED']
    return [conn['user'] for conn in this_user['edges']['connections'] if conn['type'] == connected]

def get_pending_connections(this_user):
    pending = User.connection_types['PENDING_APPROVAL']
    return [conn for conn in this_user['edges']['connections'] if conn['type'] == pending]

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


def request_connection(other_user, message):
    conn_type = connection_type(other_user)
    me = findUserByID('me')

    if conn_type:
        raise Exception('user already added')

    sent_request = {'user': str(other_user._id), 'type': User.connection_types['SENT'], 'message': message, 'date':datetime.datetime.utcnow()}
    pending_approval_request = {'user': str(me._id), 'type': User.connection_types['PENDING_APPROVAL'], 'message': message, 'date':datetime.datetime.utcnow()}
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
def handle_connection(other_user, message):
    conn_type = connection_type(other_user)
    if conn_type == User.connection_types['PENDING_APPROVAL']:
        confirm_connection(other_user)
    elif conn_type == '':
        request_connection(other_user, message)
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
#KEEPS THE ORDERING OF THE LIST
def get_basic_info_from_ids(user_ids):
    user_list = []
    for user_id in user_ids:
        user_list.append(findSingleUser({'_id':user_id}))
    return get_basic_info_from_users(user_list)

# decorator that protects other users from PUT/POST/DELETE on you stuff
# user_id _must_ be passed in as 'user_id'
def only_me(function):
    def inner(*args, **kwargs):
        if kwargs['user_id'] != 'me':
            return '{}', HTTP_401_UNAUTHORIZED
        return function(*args, **kwargs)
    return inner
