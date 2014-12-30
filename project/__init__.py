#################
#### imports ####
#################

from flask import Flask
from flask import jsonify
from flask.ext.api.status import *
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from mongokit import *
from flask.ext.bcrypt import Bcrypt
from flask.ext.cors import CORS

################
#### config ####
################
connection = Connection()
Users = connection['thehookemup'].Users
ROUTE_PREPEND='/api/v1'
app = Flask(__name__)
cors = CORS(app, allow_headers=['Origin','Content-Type'],
	supports_credentials=True,
	origins='http://localhost:3000')
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

from project.users.views import users_blueprint
app.register_blueprint(users_blueprint)

login_manager.login_view = "users.login"

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(error='Unauthorized'), HTTP_401_UNAUTHORIZED

#TODO: We should probably use _id instead of email for login and out info
@login_manager.user_loader
def load_user(user_id):
    return Users.User.find_one({'email':user_id})
