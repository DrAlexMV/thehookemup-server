from project.config import config
from project.services.database import Database

db_name = raw_input('Enter the DB name on which you wish to operate: ')
config['DATABASE_NAME'] = db_name
Database.connect(config)

import models.invite
import models.user


def make_invite():
    inv = models.invite.create_invite(None)
    print 'New invite code is: ', inv['code']


def set_permission(user_id, level):
    user_data = models.user.findUserByID(user_id)
    user_data['permissionLevel'] = level
    user_data.save()
