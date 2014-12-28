from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session
from flask.ext.login import login_user, login_required, logout_user
from project import bcrypt, ROUTE_PREPEND
import models
from flask_oauth import OAuth

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


@users_blueprint.route(ROUTE_PREPEND+'/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
       req = request.json
       request_email = req['email']
       request_password = req['password']
       entry = models.Users.User.find_one({'email':request_email})
       print request_email
       if entry != None:
           if bcrypt.check_password_hash(entry['password'],request_password):
               #login_user(user)
               return jsonify(loggedIn = True, errors = None)
           else:
               error = 'Invalid password'
       else:
           error = 'Invalid email'

       return jsonify(LoggedIn=False, errors=error)
    else:
        #?? Render the template client side. What should i return here?
        return render_template('test.html', error=None)


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
       request_password = req['password']
       request_name = req['name']
       entry = models.Users.User.find_one({'email':request_email})
       if entry == None:
           user = models.createUser(request_name, request_email, request_password)
           user.save()
           #login_user(user)
           return jsonify(loggedIn = True, errors = None)
       else:
           error = 'Email is already in use'
           return jsonify(LoggedIn=False, errors=error)
    else:
        #?? Render the template client side. What should i return here?
        return render_template('test.html', error=None)


@users_blueprint.route(ROUTE_PREPEND+'/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return jsonify(LoggedIn=False, errors=None)


####################################################
####################################################

#UserBasicInfo: /api/user/{userid}/
#UserDetails: /api/user/{userid}/details/
#UserEdges: /api/user/{userid}/edges/

@users_blueprint.route(ROUTE_PREPEND+'/user/{userid}', methods=['GET'])
def getUserBasicInfo():
    http_get_name = request.args.get('email', 'Anonymous')
    logout_user()
    return jsonify(LoggedIn=False, errors=None)
