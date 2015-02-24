from bson import ObjectId
from flask_login import current_user
from flask_mongokit import Document
from models.user import findMultipleUsers, findUserByID
from project.services.database import Database
from project.config import config
from project.services.auth import Auth

connection = Database.connection()
Admins = Database['Admins']

@connection.register
class Admin(Document):
    __collection__ = 'Admins'
    __database__ = config['DATABASE_NAME']

    structure = {
        "activatedBy": ObjectId
    }


def basic_user_with_email(user):
    basic_user = user.to_basic()
    basic_user["email"] = user["email"]
    return basic_user


def activate_user(user_id):
    user = findUserByID(user_id)
    user["permissionLevel"] = Auth.USER
    user.save()
    return basic_user_with_email(user)


def elevate_user_to_admin(user_id):
    user_to_elevate = findUserByID(user_id)
    user_to_elevate["permissionLevel"] = Auth.ADMIN
    user_to_elevate.save()
    return user_to_elevate


def create_admin_settings(user_id):
    attributes = {
        "_id": ObjectId(user_id),
        "activatedBy": ObjectId(current_user["_id"])
    }

    new_admin_settings = Admins.Admin(attributes)
    elevated_user = elevate_user_to_admin(user_id)

    new_admin_settings.save()

    return new_admin_settings, elevated_user


def elevate_admin_to_super_admin(admin_id):
    pass


def find_unactivated_users():
    return [basic_user_with_email(user) for user in findMultipleUsers({"permissionLevel": Auth.GHOST})]


