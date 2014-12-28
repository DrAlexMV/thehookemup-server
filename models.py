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
                'company name': basestring,
                'start date': basestring,
                'end date':  basestring,
                'description': basestring,
                'currently working': bool
                }],
        'edges': {
			'connections': [int],
			'associations': [int]
		}

    }
    required_fields = ['name', 'email', 'password', 'date_joined']
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

def createUser(name, email, password):
    user = Users.User()
    user['name']=name
    user['email']=email
    user['password']= bcrypt.generate_password_hash(password)
    return user

def addJob(user, companyName, startDate, description, currentlyWorking):
    job = {
        'company':companyName,
        'startDate':startDate,
        'description':description,
        'currentlyWorking':currentlyWorking
    }
    user['jobs'].append(job)


def addDetail(user, title, content):
    detail = {
        'title':title,
        'content':content
    }
    user.details.append(detail)



# register the User document with our current connection
