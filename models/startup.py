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
        'website': basestring,
        'description': basestring,
        'picture': basestring,  # picture mongo id
        'owners': [basestring],  # only one for now, add more later
        'markets': [basestring],  # ids of markets
        'handles': [{'type': basestring, 'url': basestring}],
        'wall': [{
            'id': basestring,
            'user': ObjectId,
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
        'people': [basestring],
        'overview': basestring
    }

    use_dot_notation = True

    question_status = {'PENDING_ANSWER': 'pa', 'ANSWERED': 'a'}

    required_fields = ['name', 'description']

    basic_info_fields = {'name', 'date', 'website', 'handles', 'description', 'picture', 'owners', 'markets', '_id'}

    def to_searchable(self):
        return {
            "name": self.name,
            "website": self.website,
            "description": self.description
        }

    def __repr__(self):
        return '<Startup %r>' % (self.name)


def is_owner(user_id, startup_object):
    return str(user_id) in startup_object.owners


def create_startup(user_id, request):
    startup = Startups.Startup()
    utils.mergeFrom(request, startup, Startup.required_fields)
    startup.date = datetime.datetime.utcnow()
    startup.owners.append(str(user_id))
    startup.people.append(str(user_id))

    optional = Startup.basic_info_fields.difference(Startup.required_fields)
    optional.remove('_id')

    utils.mergeFrom(request, startup, optional, require=False)

    database_wrapper.save_entity(startup)
    return startup


def find_startup_by_id(startup_id):
    #takes a string id
    startup = Startups.Startup.find_one({'_id': ObjectId(startup_id)})
    return startup

def get_basic_startup_by_id(startup_id):
    return get_basic_startup(find_startup_by_id(startup_id))

def get_basic_startup(startup_object, current_user_id=None):
    fields = list(Startup.basic_info_fields)
    current_user_id = current_user_id if current_user_id else user.getUserID('me')
    owner = {'isOwner': is_owner(current_user_id, startup_object)}
    return utils.jsonFields(startup_object, fields, response=False, extra=owner)


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

    for qa_item in qa:
        asker_user = user.findUserByID(ObjectId(qa_item['asker']))
        qa_item['asker'] = utils.jsonFields(asker_user, user.User.basic_info_fields, response=False)

    all_people_needed = set()
    annotated_wall = []
    for wall_item in startup_object.wall:
        all_people_needed.add(wall_item['user'])
        annotated_wall_item = wall_item.copy()
        annotated_wall_item['user'] = str(annotated_wall_item['user'])
        annotated_wall.append(annotated_wall_item)

    users = {}
    for basic_info in user.get_basic_info_from_ids(list(all_people_needed)):
        users[basic_info['_id']] = basic_info

    for wall_item in annotated_wall:
        wall_item['user'] = utils.jsonFields(users[wall_item['user']], user.User.basic_info_fields, response=False)

    people_info = user.get_basic_info_from_ids(map(ObjectId, startup_object.people))
    return {'qa': qa, 'wall': annotated_wall, 'people': people_info, 'overview': startup_object.overview}


def post_wall(startup_object, request, current_user_id):
    msg = {'user': current_user_id, 'message': request['message'], 'date': datetime.datetime.utcnow(), 'id': str(ObjectId())}
    startup_object.wall.insert(0, msg)

    database_wrapper.save_entity(startup_object)

    msg['user'] = utils.jsonFields(user.findUserByID(current_user_id), user.User.basic_info_fields, response=False)
    return msg


def remove_wall(startup_object, post_id, request):
    index = 0
    while index < len(startup_object.wall):
        if startup_object.wall[index]['id'] == post_id:
            startup_object.wall.pop(index)
            database_wrapper.save_entity(startup_object)
            return startup_object
        index += 1

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

    startup_object.qa.insert(0, question)
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
        index += 1

    raise Exception('Not found')


def put_people(startup_object, request):
    startup_object.people = request['people']
    database_wrapper.save_entity(startup_object)
    return startup_object

def put_overview(startup_object, request):
    startup_object.overview = request['overview']
    database_wrapper.save_entity(startup_object)
    return startup_object
