#################
#### imports ####
#################

from flask import Flask
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager

import os

################
#### config ####
################

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
db = MongoKit(app)
db.register([Task])
#app.config.from_object(os.environ['APP_SETTINGS'])


from project.users.views import users_blueprint
app.register_blueprint(users_blueprint)
'''
from project.home.views import home_blueprint
from project.admin.views import admin_blueprint

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint)


'''

'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()
'''