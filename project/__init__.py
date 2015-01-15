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
from elasticsearch import Elasticsearch
from config import config

################
#### config ####
################


# connect to Mongo
print 'connecting to mongodb at: %s %i' % (config['MONGODB_HOST'], config['MONGODB_PORT'])
DATABASE_NAME = 'thehookemup'
connection = Connection(config['MONGODB_HOST'],
                        config['MONGODB_PORT'])
Users = connection[DATABASE_NAME].Users
DatabaseImages = connection[DATABASE_NAME].DatabaseImages

# Elastic
print 'connecting to elastic search at: %s %i' % (config['ELASTIC_HOST'], config['ELASTIC_PORT'])
es = Elasticsearch([config['ELASTIC_HOST']],
                   port=config['ELASTIC_PORT'])

init_elastic.generate_search_structure(es)


#misc configuration
ROUTE_PREPEND='/api/v1'
app = Flask(__name__)
cors = CORS(app, allow_headers=['Origin','Content-Type', 'Cache-Control', 'X-Requested-With'],
	supports_credentials=True,
	origins=config['ACCEPTED_ORIGINS'])
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)


#register the blueprints
from project.users.views import users_blueprint
from project.images.views import images_blueprint
from project.search.views import search_blueprint
app.register_blueprint(users_blueprint)
app.register_blueprint(images_blueprint)
app.register_blueprint(search_blueprint)


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
