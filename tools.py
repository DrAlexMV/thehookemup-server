from project.config import config
from project.services.database import Database

Database.connect(config)

import models.invite


def make_invite():
    inv = models.invite.create_invite(None)
    print 'New invite code is: ', inv['code']
