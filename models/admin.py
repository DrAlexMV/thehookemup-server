from models.base_user import BaseUser
from models.user import findMultipleUsers, findUserByID, get_basic_info_with_security
from project import config, Database
from base_user import prepare
from project.services.auth import Auth

connection = Database.connection()
Admins = Database['Admins']

@connection.register
class Admin(BaseUser):
    __collection__ = 'Admins'
    __database__ = config['DATABASE_NAME']

    structure = {}

    default_values = {}

    def get_access_level(self):
        return Auth.ADMIN if self['activated'] else Auth.GHOST


def basic_user_with_email(user):
    basic_user = user.to_basic()
    basic_user["email"] = user["email"]
    return basic_user


def create_admin(attributes):
    new_admin = Admins.Admin(prepare(attributes))
    new_admin.save()
    return new_admin


def activate_user(user_id):
    user = findUserByID(user_id)
    user.activate()
    user.save()
    return basic_user_with_email(user)


def find_unactivated_users():
    return [basic_user_with_email(user) for user in findMultipleUsers({"activated": False})]


