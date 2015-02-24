from project import database_wrapper
from bson.objectid import ObjectId
from project import utils
from mongokit import Document
from models import user, search_results, market
import datetime
from project.config import config
from project.services.elastic import Elastic
from project.services.database import Database

Startups = Database['Startups']
connection = Database.connection()
es = Elastic.connection()


@connection.register
class Startup(Document):
    __collection__ = 'Startups'
    __database__ = config['DATABASE_NAME']
    structure = {
        'type': basestring,
        'name': basestring,
        'date': datetime.datetime,
        'website': basestring,
        'description': basestring,
        'picture': basestring,  # picture mongo id
        'owners': [basestring],  # only one for now, add more later
        'markets': [ObjectId],  # ids of markets
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

    basic_info_fields = {'name', 'date', 'website', 'handles', 'description', 'picture', 'owners', '_id'}

    default_values = {
        "type": "startup"
    }

    def to_searchable(self):
        return {
            "name": self.name,
            "website": self.website,
            "description": self.description,
            "markets":[market['name'] for market in get_markets_from_id(self.markets)]
        }

    def __repr__(self):
        return '<Startup %r>' % (self.name)

def get_markets_from_name(list_of_market_name):
    if list_of_market_name is None:
        return []
    output = []
    for name in list_of_market_name:
        found_market = market.find_market({"name": name})
        if found_market is None:
            #need to create a new market
            output.append(market.create_market(name, 0))
        else:
            output.append(found_market)
    return output

def get_markets_from_id(list_of_market_id):
    if list_of_market_id is None:
        return []
    output = []
    for id in list_of_market_id:
        output.append(market.find_market_by_id(id))
    return output


def put_markets(startup,req):
    markets = req.get('markets')
    previous_markets_list = get_markets_from_id(startup['markets'])
    put_markets_list = get_markets_from_name(markets)
    removed_markets = set(previous_markets_list).difference(put_markets_list)
    added_markets = set(put_markets_list).difference(previous_markets_list)
    for removed_market in removed_markets:
        if removed_market is None:
            #this should never happen
            raise Exception("Startup had reference to market that doesn't exist")
        else:
            market.decrement_market(removed_market)

    for added_market in added_markets:
        if added_market is None:
            #this should never happen
            raise Exception("Something broke.. Added market is None?!")
        else:
            market.increment_market(added_market)
    startup.markets = [put_market._id for put_market in put_markets_list]
    database_wrapper.save_entity(startup)
    return True



def is_owner(user_id, startup_object):
    return str(user_id) in startup_object.owners


def create_startup(user_id, request):
    startup = Startups.Startup()
    utils.mergeFrom(request, startup, Startup.required_fields)
    startup.date = datetime.datetime.utcnow()
    startup.owners.append(str(user_id))
    startup.people.append(str(user_id))
    print("here before put!!!")
    #convert the market names in the request into market ids
    put_markets(startup, request)
    print("here after put")
    optional = Startup.basic_info_fields.difference(Startup.required_fields)
    optional.remove('_id')
    utils.mergeFrom(request, startup, optional, require=False)
    database_wrapper.save_entity(startup)
    return startup


def find_startup_by_id(startup_id):
    #takes a string id
    startup = Startups.Startup.find_one({'_id': ObjectId(startup_id)})
    return startup

def find_multiple_users(mapAttributes):
    entries = Startups.Startup.find(mapAttributes)
    return entries

def get_basic_startup_by_id(startup_id):
    return get_basic_startup(find_startup_by_id(startup_id))


def get_basic_startups_from_ids(startup_ids, keep_order=False):
    queried = find_multiple_users({'_id': {'$in': startup_ids}})
    if (keep_order):
        by_id = {startup._id : startup for startup in queried}
        sorted_queried = []
        for startup_id in startup_ids:
            startup_data = by_id.get(startup_id)
            if (startup_data):
                sorted_queried.append(startup_data)
            else:
                print 'Warning, Orphaned reference ', startup_id
        return [ get_basic_startup(startup_info) for startup_info in sorted_queried ]

    return [ get_basic_startup(startup_info) for startup_info in sorted_queried ]

def get_basic_startup(startup_object, current_user_id=None):
    fields = list(Startup.basic_info_fields)
    current_user_id = current_user_id if current_user_id else user.getUserID('me')
    owner = {'isOwner': is_owner(current_user_id, startup_object)}
    output = utils.jsonFields(startup_object, fields, response=False, extra=owner)
    #append the string names for the markets to the basic info
    output['markets'] = [str(market['name']) for market in get_markets_from_id(startup_object['markets'])]
    return output

def update_basic_startup(startup_object, request):
    fields = list(Startup.basic_info_fields)
    fields.remove('_id')
    utils.mergeFrom(request, startup_object, fields, require=False)
    #put the object ids for all the markets in the request into the startup
    startup_object['markets']=[market._id for market in get_markets_from_name(startup_object['markets'])]
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


def simple_search(query_string, results_per_page, page):
    """
    Takes a string of space separated words to query, returns a list
    of  startups that have those keywords in any fields.
    This is to be used when filter params are not specified.
    """
    if query_string is None:
        #simple query to get all results
        query = {
            "query": {
                "match_all": {}
            }
        }
    else:
        query = {
                "query":{
                    "multi_match": { #match against multiple fields
                    "query":                query_string, #string that was entered in. automatically parsed into words
                    "fuzziness": 3,  #Levenshtein Edit Distance
                    "type":                 "most_fields", #combine the score of all matching fields
                    "fields":               ['_all'], #match against all indexed fields
                    "minimum_should_match": "5%" #at least 5% of the words in query_string should match somewhere
                }
            }
        }
    if page is None or results_per_page is None:
        res = es.search(index=config['DATABASE_NAME'], doc_type='Startup', body=query)['hits']['hits']
    else:
        res = es.search(index=config['DATABASE_NAME'], doc_type='Startup', body=query, from_=page*results_per_page, size=results_per_page)['hits']['hits']
    number_results = es.count(index=config['DATABASE_NAME'], doc_type='Startup', body=query)['count']
    return search_results.SearchResults(res,{'numberResults': number_results})
