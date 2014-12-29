from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response
from flask.ext.login import login_user, login_required, logout_user, abort
from project import bcrypt, ROUTE_PREPEND
from flask.ext.api import FlaskAPI, status, exceptions
import json
import models
from flask_oauth import OAuth
from bson.objectid import ObjectId
import sys

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
        return jsonify(error=str(e)),status.HTTP_400_BAD_REQUEST
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
       return jsonify(LoggedIn=False, error=error)

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


@users_blueprint.route(ROUTE_PREPEND+'/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        req = request.json
        request_email = req['email']
        entry = models.findSingleUser({'email':request_email})
        if entry == None:
            try:
                user = models.createUser(req)
            except:
                e = sys.exc_info()[0]
                return jsonify(error=str(e)),status.HTTP_400_BAD_REQUEST
            user.save()
            #login_user(user)
            return jsonify(loggedIn = True, error = None)
        else:
            error = 'Email is already in use'
            return jsonify(LoggedIn=False, error=error)
    else:
        #?? Render the template client side. What should i return here?
        return render_template('test.html', error=None)


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
    entry = models.findSingleUser({'_id':ObjectId(userid)})
    if entry==None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            #TODO: this needs to be refactored to not save multiple times to improve speed
            for field in req:
                entry[field]=req[field]
                entry.save()
        except:
            #return jsonify(error='broken')
            return jsonify(error='Invalid key'),status.HTTP_400_BAD_REQUEST
        return '', status.HTTP_200_OK

    else:
        return jsonify(email=entry['email'], name=entry['name'], date_joined = entry['date_joined'], \
                       graduation_year=entry['graduation_year'],\
                       major = entry['major'],\
                       description = entry['description'],\
                       university=entry['university'],\
                       _id=userid,\
                       error=None)

@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/<attribute>', methods=['DELETE'])
@login_required
def delete_basic_user_info(userid, attribute):
    entry = models.findSingleUser({'_id':ObjectId(userid)})
    if entry==None:
        abort(404)
    try:
        entry[attribute]=None
        entry.save()
    except:
        #print req['details']
        print sys.exc_info()[0]
        return jsonify(error='Invalid key or field cannot be deleted'),status.HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
    return '', status.HTTP_200_OK


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details', methods=['GET', 'PUT'])
@login_required
def userDetails(userid):
    entry = models.findSingleUser({'_id':ObjectId(userid)})
    if entry==None:
        abort(404)
    if request.method == 'PUT':
        req = request.get_json()
        try:
            models.addDetail(entry,req)
        except:
            #print req['details']
            print sys.exc_info()[0]
            return jsonify(error='Invalid detail format'),status.HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
        return '', status.HTTP_200_OK
    else:
        print entry['details']
        return Response(json.dumps(entry['details']),  mimetype='application/json')


@users_blueprint.route(ROUTE_PREPEND+'/user/<userid>/details/<detail_title>', methods=['DELETE'])
@login_required
def deleteDetail(userid, detail_title):
    entry = models.findSingleUser({'_id':ObjectId(userid)})
    if entry==None:
        abort(404)
    try:
        models.removeDetail(entry,detail_title)
    except:
        #print req['details']
        print sys.exc_info()[0]
        return jsonify(error='Invalid detail format'),status.HTTP_400_BAD_REQUEST
        #return empty response with 200 status ok
    return '', status.HTTP_200_OK
