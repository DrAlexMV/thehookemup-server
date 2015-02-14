from bson.objectid import ObjectId
from project.services.database import Database
from mongokit import Document
from project import config

connection = Database.connection()
SocialSignins = Database['SocialSignins']
Users = Database['Users']


@connection.register
class SocialSigninsDocument(Document):
    __collection__ = 'SocialSignins'
    __database__ = config['DATABASE_NAME']
    structure = {
        'user': ObjectId,
        'facebook': basestring
    }


def get_user_from_social_id(social_type, social_id):
    sign_in = SocialSignins.SocialSigninsDocument.find_one({social_type: social_id})
    if sign_in is None:
        return None

    return Users.User.find_one({'_id': sign_in['user']})
