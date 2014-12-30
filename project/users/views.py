from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND, utils
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
import models
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

#TODO: these aren't set up correctly yet
FACEBOOK_APP_ID = '188477911223606'
FACEBOOK_APP_SECRET = '621413ddea2bcc5b2e83d42fc40495de'
oauth = OAuth()

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@users_blueprint.route(ROUTE_PREPEND+"/", methods=['GET', 'POST'])
@login_required
def home():
    json = request.json
    print json
    return render_template('test.html', error=None)


@users_blueprint.route(ROUTE_PREPEND+'/login', methods=['POST'])
def login():
    error = None
    req = request.json
    try:
        request_email = req['email']
        request_password = req['password']
    except:
        e = sys.exc_info()[0]
        return jsonify(error=str(e)),HTTP_400_BAD_REQUEST
    entry = models.findSingleUser({'email':request_email})
    if entry != None:
        if bcrypt.check_password_hash(entry['password'],request_password):
            login_user(entry)
            obj_id = str(entry._id)
            return userBasicInfo(obj_id)
        else:
            error = 'Invalid password'
    else:
       error = 'Invalid email'
    return jsonify(LoggedIn=False, error=error),HTTP_400_BAD_REQUEST

@users_blueprint.route(ROUTE_PREPEND+'/login/facebook', methods=['GET', 'POST'])
def login_facebook():
     return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))


@users_blueprint.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@users_blueprint.route(ROUTE_PREPEND+'/signup', methods=['POST'])
def signup():
    error = None
    req = request.json
    request_email = req['email']
    entry = models.findSingleUser({'email':request_email})
    if entry == None:
        try:
            user = models.createUser(req)
            user.save()
        except:
            e = sys.exc_info()[0]
            return jsonify(error=str(e)),HTTP_400_BAD_REQUEST
        #login_user(user)
        return jsonify(loggedIn = True, error = None, _id=str(user._id))
    else:
        error = 'Email is already in use'
        return jsonify(LoggedIn=False, error=error), HTTP_400_BAD_REQUEST


@users_blueprint.route(ROUTE_PREPEND+'/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify(LoggedIn=False, error=None)


####################################################
####################################################

#UserBasicInfo: /api/user/{userid}/
#UserDetails: /api/user/{userid}/details/
#UserEdges: /api/user/{userid}/edges/

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>', methods=['GET', 'PUT'])
@login_required
def userBasicInfo(userid):
    entry = models.findUserByID(userid)
    if entry==None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            utils.mergeFrom(req, entry, models.User.basic_info_fields, require=False)
            entry.save()
        except:
            return jsonify(error='Invalid key'),HTTP_400_BAD_REQUEST
        return '', HTTP_200_OK

    else: # GET
        return utils.jsonFields(entry, models.User.basic_info_fields)

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/<attribute>', methods=['DELETE'])
@login_required
def delete_basic_user_info(userid, attribute):
    entry = models.findUserByID(userid)
    if entry==None:
        abort(404)
    try:
        entry[attribute]=None
        entry.save()
    except:
        print sys.exc_info()[0]
        return jsonify(error='Invalid key or field cannot be deleted'),HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
    return '', HTTP_200_OK


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details', methods=['GET', 'PUT'])
@login_required
def userDetails(userid):
    entry = models.findUserByID(userid)
    if entry==None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            for detail in req:
                models.addDetail(entry, detail)
        except:
            #print req['details']
            print sys.exc_info()[0]
            return jsonify(error='Invalid detail format'),HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
        return '', HTTP_200_OK
    else:
        print entry['details']
        return Response(json.dumps(entry['details']),  mimetype='application/json')


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/<detail_title>', methods=['DELETE'])
@login_required
def deleteDetail(userid, detail_title):
    entry = models.findUserByID(userid)
    if entry==None:
        abort(404)

    if models.removeDetail(entry, detail_title):
        return '', HTTP_200_OK
    else:
        return '', HTTP_404_NOT_FOUND
