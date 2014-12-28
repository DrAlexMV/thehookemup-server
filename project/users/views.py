from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify
from flask.ext.login import login_user, login_required, logout_user
from project import bcrypt, ROUTE_PREPEND
import models


users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
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
       entry = models.collectionUsers.User.find_one({'email':request_email})
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


@users_blueprint.route(ROUTE_PREPEND+'/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
       req = request.json
       request_email = req['email']
       request_password = req['password']
       request_name = req['name']
       entry = models.collectionUsers.User.find_one({'email':request_email})
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