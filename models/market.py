from project import database_wrapper
from project.config import config
from bson.objectid import ObjectId
from project.services.database import Database
from mongokit import Document

Markets = Database['Markets']
connection = Database.connection()


@connection.register
class Market(Document):
    __collection__ = 'Markets'
    __database__ = config['DATABASE_NAME']
    structure = {
        'name': basestring,
        'occurrences': int
    }
    required_fields = ['name', 'occurrences']

    '''default_values = {
        'occurrences': 1
    }'''

    use_dot_notation = True

    def __repr__(self):
        return '<market %r>' % (self.name)


def create_market(name, occurrences):
    print("In create market")
    market = Markets.Market()
    market['name'] = name
    market['occurrences'] = occurrences
    database_wrapper.save_entity(market)
    return market


def find_market_by_id(market_id):
    # takes an object id
    market = Markets.Market.find_one({'_id': market_id})
    return market


def find_market(map_attributes):
    entry = Markets.Market.find_one(map_attributes)
    return entry


def increment_market(market):
    market.occurrences += 1
    database_wrapper.save_entity(market)


# TODO: delete markets from elastic and database if decremented to zero
def decrement_market(market):
    if market.occurrences == 1:
        database_wrapper.remove_entity(market)
    else:
        market.occurrences -= 1
        database_wrapper.save_entity(market)
