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
import init_elastic
from init_elastic import es

################
#### config ####
################


# connect to Mongo
DATABASE_NAME = 'thehookemup'
connection = Connection()
Users = connection[DATABASE_NAME].Users
DatabaseImages = connection[DATABASE_NAME].DatabaseImages

#misc configuration
ROUTE_PREPEND='/api/v1'
app = Flask(__name__)
cors = CORS(app, allow_headers=['Origin','Content-Type', 'Cache-Control', 'X-Requested-With'],
	supports_credentials=True,
	origins='http://localhost:3000')
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)


#register the blueprints
from project.users.views import users_blueprint
from project.images.views import images_blueprint
app.register_blueprint(users_blueprint)
app.register_blueprint(images_blueprint)
login_manager.login_view = "users.login"

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(error='Unauthorized'), HTTP_401_UNAUTHORIZED

@app.errorhandler(404)
def not_found(error=None):
	return jsonify(error='Not Found'), HTTP_404_NOT_FOUND

#TODO: We should probably use _id instead of email for login and out info
@login_manager.user_loader
def load_user(user_id):
    return Users.User.find_one({'email':user_id})
