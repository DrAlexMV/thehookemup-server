from mongokit import *
from project import Startups
from project import connection
from project import database_wrapper
from bson.objectid import ObjectId
from project import utils
from models import user
import datetime

@connection.register
class Startup(Document):
    __collection__ = 'Startups'
    __database__ = 'thehookemup'
    structure = {
        'name': basestring,
        'date': datetime.datetime,
        'description': basestring,
        'picture': basestring, # picture mongo id
        'owners': [basestring], # only one for now, add more later
        'categories': [basestring], # ids of categories
        'wall': [{
            'id': basestring,
            'date': datetime.datetime,
            'message': basestring # messages posted by this company
        }],
        'qa': [{ # questions and answers
            'id': basestring,
            'date': datetime.datetime,
            'status': basestring, #pending answer/approval ('pa'), approved/answered ('a')
            'asker': basestring, # user id
            'question': basestring,
            'answer': basestring # answer formulated by company
        }],
        'people': [basestring]
    }

    question_status = {'PENDING_ANSWER': 'pa', 'ANSWERED': 'a'}

    required_fields = ['name', 'description']

    basic_info_fields = {'name', 'date', 'description', 'picture', 'owners', 'categories', '_id'}

    use_dot_notation = True
    def __repr__(self):
        return '<Startup %r>' % (self.name)

def is_owner(user_id, startup_object):
    return str(user_id) in startup_object.owners

def create_startup(user_id, request):
    startup = Startups.Startup()
    utils.mergeFrom(request, startup, Startup.required_fields)
    startup.date = datetime.datetime.utcnow()
    startup.owners.append(str(user_id))
    
    optional = Startup.basic_info_fields.difference(Startup.required_fields)
    optional.remove('_id')

    utils.mergeFrom(request, startup, optional, require=False)

    database_wrapper.save_entity(startup)
    return startup

def find_startup_by_id(startup_id):
    #takes a string id
    startup = Startups.Startup.find_one({'_id': ObjectId(startup_id)})
    return startup

def get_basic_startup(startup_object):
    fields = list(Startup.basic_info_fields)
    return utils.jsonFields(startup_object, fields, response = False)

def update_basic_startup(startup_object, request):
    fields = list(Startup.basic_info_fields)
    fields.remove('_id')
    utils.mergeFrom(request, startup_object, fields, require=False)

    database_wrapper.save_entity(startup_object)
    return startup_object

def get_details(startup_object, current_user_id):
    qa = startup_object.qa
    if not is_owner(current_user_id, startup_object):
        # get only answered messages
        qa = filter(lambda q: q['status'] == Startup.question_status['ANSWERED'], qa)

    people_info = user.get_basic_info_from_ids(map(ObjectId, startup_object.people))
    return {'qa': qa, 'wall': startup_object.wall, 'people': people_info}

def post_wall(startup_object, request):
    msg = {'message': request['message'], 'date': datetime.datetime.utcnow(), 'id': str(ObjectId())}
    startup_object.wall.insert(0, msg)

    database_wrapper.save_entity(startup_object)

    return startup_object

def remove_wall(startup_object, post_id, request):
    index = 0
    while index < len(startup_object.wall):
        if startup_object.wall[index]['id'] == post_id:
            startup_object.wall.pop(index)
            database_wrapper.save_entity(startup_object)
            return startup_object

    raise Exception('Not found')

def add_question(startup_object, request, current_user_id):
    question = {
        'question': request['question'],
        'answer': '',
        'date': datetime.datetime.utcnow(),
        'status': Startup.question_status['PENDING_ANSWER'],
        'id': str(ObjectId()),
        'asker': str(current_user_id)
    }

    startup_object.qa.append(question)
    database_wrapper.save_entity(startup_object)

    return startup_object

def give_answer(startup_object, question_id, request):
    for question in startup_object.qa:  # O(N). Probably not too bad.
        if question['id'] == question_id:
            question['answer'] = request['answer']
            question['status'] = Startup.question_status['ANSWERED']
            database_wrapper.save_entity(startup_object)
            return startup_object

    raise Exception('Not found')

def remove_question(startup_object, question_id, request):
    index = 0
    while index < len(startup_object.qa):
        if startup_object.qa[index]['id'] == question_id:
            startup_object.qa.pop(index)
            database_wrapper.save_entity(startup_object)
            return startup_object

    raise Exception('Not found')

def put_people(startup_object, request):
    startup_object.people = request['people']
    database_wrapper.save_entity(startup_object)
    return startup_object
