from mongokit import *
from project import bcrypt
import datetime


connection = Connection()
Users = connection['thehookemup'].Users



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
        'name': basestring,
        'email': basestring,
        'password': basestring,
        'date_joined': datetime.datetime,
        'graduation_year': basestring,
        'major': basestring,
        'description': basestring,
        'university': basestring,
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
			'connections': [int],
			'associations': [int]
		}

    }
    required_fields = ['name', 'email', 'password', 'date_joined', 'graduation_year', 'major', 'description','university']
    default_values = {
        'date_joined': datetime.datetime.utcnow
    }
    validators = {
        'name': max_length(50),
        'email': max_length(120),
        'password': max_length(120)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.name)

    #### Required to be implemented for login manager ####

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.email)

    ######################################################

def createUser(jsonAttributes):
        user = Users.User()
        user['name']=jsonAttributes['name']
        user['email']=jsonAttributes['email']
        user['password']= bcrypt.generate_password_hash(jsonAttributes['password'])
        user['graduation_year']=jsonAttributes['graduation_year']
        user['major']=jsonAttributes['major']
        user['description']=jsonAttributes['description']
        user['university']=jsonAttributes['university']
        return user

def addJob(user, jsonAttributes):
    user['jobs'].append(jsonAttributes)

#TODO: fix this up
def addDetail(user, title, content):
    detail = {
        'title':title,
        'content':content
    }
    user.details.append(detail)

def findSingleUser(mapAttributes):
    entry = Users.User.find_one(mapAttributes)
    return entry

def findMultipleUsers(mapAttributes):
    entries = Users.User.find(mapAttributes)
    return entries


# register the User document with our current connection
