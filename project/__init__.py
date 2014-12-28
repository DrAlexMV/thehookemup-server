#################
#### imports ####
#################

from flask import Flask
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from mongokit import *
from flask.ext.bcrypt import Bcrypt

################
#### config ####
################

ROUTE_PREPEND='/api/v1'
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

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