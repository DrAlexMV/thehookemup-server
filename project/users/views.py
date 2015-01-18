from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND, utils, database_wrapper
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
import json
from models import user
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

#TODO: these aren't set up correctly yet
FACEBOOK_APP_ID = '188477911223606'
FACEBOOK_APP_SECRET = '621413ddea2bcc5b2e83d42fc40495de'
oauth = OAuth()

users_blueprint = Blueprint(
    'users', __name__
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
    entry = user.findSingleUser({'email': request_email})
    if entry is not None:
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
    entry = user.findSingleUser({'email': request_email})
    if entry is None:
        try:
            new_user = user.createUser(req)
            database_wrapper.save_entity(new_user)
        except Exception as e:
            return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
        login_user(new_user)
        return userBasicInfo(str(new_user._id))
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

@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>', methods=['PUT'])
@login_required
@user.only_me
def userBasicInfo(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        abort(404)

    req = request.get_json()
    try:
        utils.mergeFrom(req, entry, user.User.basic_info_fields, require=False)
        database_wrapper.save_entity(entry)
    except:
        return jsonify(error='Invalid key'), HTTP_400_BAD_REQUEST
    return '', HTTP_200_OK


@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>', methods=['GET'])
@login_required
def userBasicInfo(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        abort(404)
    return user.get_basic_info_with_security(entry)

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/<attribute>', methods=['DELETE'])
@login_required
def delete_basic_user_info(userid, attribute):
    entry = user.findUserByID(userid)
    if entry is None:
        abort(404)
    try:
        entry[attribute] = None
        database_wrapper.save_entity(entry)
    except:
        print sys.exc_info()[0]
        return jsonify(error='Invalid key or field cannot be deleted'), HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
    return '', HTTP_200_OK


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details', methods=['GET'])
@login_required
def get_user_details(userid):
    """


    """
    try:
        entry = user.findUserByID(userid)
        if entry is None:
            return '', HTTP_404_NOT_FOUND
        return user.get_user_details(entry)
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/skills', methods=['PUT'])
@login_required
def put_skills(userid):
    """
    Example request:

    PUT
    {
    "skills":["popping molly", "javascript"]
    }

    returns STATUS_200_OK when successful
    """
    try:
        req = request.get_json()
        entry = user.findUserByID(userid)
        if entry is None:
            return '', HTTP_404_NOT_FOUND
        if user.put_skills(entry, req):
            return '', HTTP_200_OK
        else:
            return '', HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/interests', methods=['PUT'])
@login_required
def put_interests(userid):
    """
    Example request:

    PUT
    {
     "interests":[{"title":"some title", "description":"some description"},
               {"title":"some title 2", "description":"some description 2"}]
    }

    returns STATUS_200_OK when successful
    """
    try:
        req = request.get_json()
        entry = user.findUserByID(userid)
        if entry is None:
            return '', HTTP_404_NOT_FOUND
        if user.put_interests(entry, req):
            return '', HTTP_200_OK
        else:
            return '', HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/projects', methods=['PUT'])
@login_required
def put_projects(userid):
    """
    Example request:

    PUT
    {
    "projects":[{
            "date": "May 2015",
            "title": "some project title",
            "description": "some project description",
            "details": [{
                "title": "some project detail title",
                "description": "some project detail description"
                        }],
            "people":["54b797090adfa96230c2c1bb"]
        }]
    }

    returns status 200_OK when successful
    """
    try:
        req = request.get_json()
        entry = user.findUserByID(userid)
        if entry is None:
            return '', HTTP_404_NOT_FOUND
        if user.put_projects(entry, req):
            return '', HTTP_200_OK
        else:
            return '', HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>/edges', methods=['GET'])
@login_required
def userEdges(user_id):
    entry = user.findUserByID(user_id)
    if entry==None:
        abort(404)

    suggested_connections = []
    pending_connections = []

    if user_id == 'me':
        suggested_connection_users = user.get_suggested_connections(entry)
        suggested_connections = user.get_basic_info_from_users(suggested_connection_users)

        pending_connection_ids = map(ObjectId, user.get_pending_connections(entry))
        pending_connections = user.get_basic_info_from_ids(pending_connection_ids)

    connection_ids = map(ObjectId, user.get_connections(entry))
    connections = user.get_basic_info_from_ids(connection_ids)

    annotated = {'connections': connections,
                 'suggestedConnections': suggested_connections,
                 'pendingConnections': pending_connections,
                 'associations': []}

    return jsonify(**annotated)

@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>/edges/connections', methods=['POST'])
@login_required
def add_connection_route(user_id):
    if user_id != 'me':
        raise Exception('Not able to add users for other people')

    req = request.get_json()

    # TODO: have some system so friend requests are sent
    connection_id = req.get('user')
    connection_message = req.get('message')

    if connection_id is None:
        return jsonify(error='missing field \'user\''), HTTP_400_BAD_REQUEST

    other_user = user.findUserByID(connection_id)

    if other_user is None:
        return jsonify(error='bad user'), HTTP_400_BAD_REQUEST

    try:
        ## TODO: improve specificity of errors
        user.handle_connection(other_user, connection_message)
        return '{}', HTTP_200_OK
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR

@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>/edges/connections/<connection_id>', methods=['DELETE'])
@login_required
def remove_connection_route(user_id, connection_id):
    entry = user.findUserByID(user_id)
    connection = user.findUserByID(connection_id)
    if entry is None or connection is None:
        abort(404)

    try:
        ## TODO: improve specificity of errors
        user.remove_user_connection(connection)
        return '{}', HTTP_200_OK
    except Exception as e:
        return jsonify(error=str(e)), HTTP_500_INTERNAL_SERVER_ERROR
