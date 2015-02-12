from flask import Flask
from flask import jsonify
from flask.ext.api.status import *
from flask.ext.login import LoginManager
from json_rest import CustomJSONEncoder

from config import config

from project.services.database import Database
from project.services.elastic import Elastic
from project.services.auth import Auth
from project.services.cors import Cors
from project.services.api import API

app = Flask(__name__)

Cors.init_app(app, config)

app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = config['SECRET_KEY']
app.debug = config['DEBUG']
app.json_encoder = CustomJSONEncoder

# Init services
Database.connect(config)

Elastic.connect(config)

Auth.init_app(app, config)

API.configure(config)

API.register_blueprints(app, config)

@app.errorhandler(404)
def not_found(error=None):
    return jsonify(error='Not Found'), HTTP_404_NOT_FOUND
