__author__ = 'austinstone'

from mongokit import *
from project import Waitlists
from project import connection
from bson.objectid import ObjectId
import datetime
from project import utils
import pymongo


@connection.register
class Waitlist(Document):
    __collection__ = 'Waitlists'
    __database__ = 'thehookemup'
    structure = {
        'email': basestring,
        'firstName': basestring,
        'lastName': basestring,
        'date': datetime.datetime,
    }
    
    required_fields = ['email', 'firstName', 'lastName']

    default_values = {
        'date': datetime.datetime.utcnow
    }

    use_dot_notation = True

    def __repr__(self):
        return '<Waitlist %r>' % self.email


def create_waitlist(json_attributes):
    waitlist = Waitlists.Waitlist()
    json_attributes['email'] = json_attributes['email'].lower()
    utils.mergeFrom(json_attributes, waitlist, Waitlist.required_fields)
    waitlist.save()
    return waitlist


def get_waitlist_attributes(waitlist):
    output = {}
    for field in Waitlist.required_fields:
        output[field] = waitlist[field]
    output['date'] = waitlist['date']

    return output


def find_waitlist_by_id(waitlist_id):
    #takes a string id
    entry = Waitlists.Waitlist.find_one({'_id': ObjectId(waitlist_id)})
    return entry


def find_waitlist(map_attributes):
    entry = Waitlists.Waitlist.find_one(map_attributes)
    return entry


def find_multiple_waitlists(map_attributes):
    entries = Waitlists.Waitlist.find(map_attributes).sort('date', pymongo.ASCENDING)
    return entries
