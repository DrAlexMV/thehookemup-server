from mongokit import *
from project import bcrypt
import datetime
from project import connection
from project import Users
from project import utils
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
        'first_name': basestring,
        'last_name': basestring,
        'email': basestring,
        'password': basestring,
        'date_joined': datetime.datetime,
        'graduation_year': basestring,
        'major': basestring,
        'description': basestring,
        'university': basestring,
        'role': basestring,
        'details':[{
            'title':basestring,
            'content':[{
                   'title': basestring,
                   'description': basestring,
                   'subpoints':[{
                       'title':basestring,
                       'description':basestring
                                }]

               }]
        }],
        'jobs':[{
                'company_name': basestring,
                'start_date': basestring,
                'end_date':  basestring,
                'description': basestring,
                'currently_working': bool
                }],
        'edges': {
            'connections': [basestring],
            'associations': [basestring]
        }

    }
    required_fields = ['first_name','last_name', 'email', 'password', 'role']
    
    basic_info_fields = [
        'first_name',
        'last_name',
        'email',
        'date_joined',
        'role',
        'graduation_year',
        'major',
        'university',
        'description',
        '_id'
    ]

    default_values = {
        'date_joined': datetime.datetime.utcnow
    }
    validators = {
        'first_name': max_length(50),
        'last_name': max_length(50),
        'email': max_length(120),
        'password': max_length(120)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.first_name)

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
    #jsonAttributes = jsonAttributes[:]
    user = Users.User()
    # swizzle password here
    jsonAttributes['password'] = bcrypt.generate_password_hash(jsonAttributes['password'])

    utils.mergeFrom(jsonAttributes, user, User.required_fields)

    not_required = ['graduation_year', 'major', 'university', 'description']
    utils.mergeFrom(jsonAttributes, user, not_required, require=False)

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

    user.save()

def removeDetail(user, detail_title):
    i = 0
    for detail in user['details']:
        if detail['title'] == detail_title:
            user['details'].pop(i)
            user.save()
            return True
        i=i+1
    return False

def updateEdges(user, new_edges):
    utils.mergeFrom(new_edges, user['edges'], ['associations', 'connections'])
    user.save()

## Like FindSingleUser but takes a string.
def findUserByID(userid):
    if userid == 'me':
        uid = current_user._id
    else:
        try:
            uid = ObjectId(userid)
        except:
            return None

    entry = Users.User.find_one({'_id': uid})
    return entry

def findSingleUser(mapAttributes):
    entry = Users.User.find_one(mapAttributes)
    return entry

def findMultipleUsers(mapAttributes):
    entries = Users.User.find(mapAttributes)
    return entries



# register the User document with our current connection
