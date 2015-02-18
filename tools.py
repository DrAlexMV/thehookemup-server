from project.config import config
from project.services.database import Database

db_name = raw_input('Enter the DB name on which you wish to operate: ')
config['DATABASE_NAME'] = db_name
Database.connect(config)

import models.invite


def make_invite():
    inv = models.invite.create_invite(None)
    print 'New invite code is: ', inv['code']
