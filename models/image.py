from mongokit import Document
from project.services.database import Database
from project import utils
import bson
import datetime
from bson.objectid import ObjectId

DatabaseImages = Database['DatabaseImages']
connection = Database.connection()

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

@connection.register
class DatabaseImage(Document):
    __collection__ = 'DatabaseImages'
    __database__ = 'thehookemup'
    structure = {
        'data': bson.binary.Binary,
        'created': datetime.datetime,
        'owner': basestring
    }

    required_fields = ['owner']

    default_values = {
        'created': datetime.datetime.utcnow
    }

    validators = {}

    use_dot_notation = True
    def __repr__(self):
        return '<DatabaseImage created on %s>' % (self.created)

def create_image(image_blob, userid):
    image = DatabaseImages.DatabaseImage()
    image['data'] = bson.Binary(image_blob)
    image['owner'] = str(userid)
    image.save()
    return image['_id']

def find_image_by_id(image_id):
    return DatabaseImages.DatabaseImage.find_one({'_id': ObjectId(image_id)})

