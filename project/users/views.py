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

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>', methods=['GET', 'PUT'])
@login_required
def userBasicInfo(userid):
    entry = user.findUserByID(userid)
    if entry is None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            utils.mergeFrom(req, entry, user.User.basic_info_fields, require=False)
            database_wrapper.save_entity(entry)
        except:
            return jsonify(error='Invalid key'), HTTP_400_BAD_REQUEST
        return '', HTTP_200_OK

    else:
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


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details', methods=['GET', 'PUT', 'PATCH'])
@login_required
def userDetails(userid):
    """
    PUT request:

    Takes an array of details, adds the details to the list of user details if the titles are unique,
    otherwise returns an error if they are not unique. An example PUT request is:
    PUT
    [{
        "title": "basestring",
        "content": [{
            "title": "basestring",
            "description": "basestring",
            "subpoints": [{
                "title": "basestring",
                "description": "basestring"
            }]

        }]
    }]


    PATCH request:
    PATCH request modifies an existing detail(s). The patch request must pass the full detail in a field named "detail"


    PATCH
    [{
        "title": "basestring",
        "content": [{
            "title": "basestring",
            "description": "basestring",
            "subpoints": [{
                "title": "basestring",
                "description": "basestring"
            }]

        }]
    }]

    A GET request simply returns the entire list of user details.

    """
    entry = user.findUserByID(userid)
    if entry is None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            user.update_details(entry, req, patch = False)
        except Exception as e:
             return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
        return '', HTTP_200_OK
    elif request.method=='PATCH':
        req = request.get_json()
        try:
            user.update_details(entry, req, patch = True)
        except Exception as e:
             return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
        return '', HTTP_200_OK
    else:
        return Response(json.dumps(entry['details']),  mimetype='application/json')

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/<detail_title>', methods=['DELETE'])
@login_required
def deleteDetail(userid, detail_title):
    entry = user.findUserByID(userid)
    if entry is None:
        abort(404)

    if user.removeDetail(entry, detail_title):
        return '', HTTP_200_OK
    else:
        return '', HTTP_404_NOT_FOUND

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/edges', methods=['GET'])
@login_required
def userEdges(userid):
    entry = user.findUserByID(userid)
    if entry==None:
        abort(404)

    user_ids = map(ObjectId, entry['edges']['connections'])
    annotated = {'connections': user.get_basic_info_from_ids(user_ids),
                 'associations': entry['edges']['associations']}

    return jsonify(**annotated)

@users_blueprint.route(ROUTE_PREPEND+'/user/<user_id>/edges/connections', methods=['POST'])
@login_required
def add_connection_route(user_id):
    entry = user.findUserByID(user_id)
    if entry is None:
        abort(404)

    req = request.get_json()
    # TODO: have some system so friend requests are sent
    connection_id = req.get('user')
    if connection_id is None:
        return jsonify(error='missing field \'user\''), HTTP_400_BAD_REQUEST

    connection = user.findUserByID(connection_id)

    if connection is None or str(connection['_id']) == str(entry['_id']):
        return jsonify(error='bad user'), HTTP_400_BAD_REQUEST

    try:
        ## TODO: improve specificity of errors
        user.add_connection(entry, connection)
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
        user.remove_connection(entry, connection)
        return '{}', HTTP_200_OK
    except:
        return '{}', HTTP_500_INTERNAL_SERVER_ERROR
