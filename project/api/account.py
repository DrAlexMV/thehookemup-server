from flask import request, jsonify, Blueprint
from project.services.auth import Auth, current_user, SocialSignin
from models import user, invite
from flask_api.status import HTTP_400_BAD_REQUEST
from project import database_wrapper

blueprint = Blueprint(
    'account', __name__
)


@blueprint.route('/login', methods=['POST'])
def login():
    req = request.json
    try:
        email = req['email'].lower()
        password_hash = req['password']
    except:
        return '', HTTP_400_BAD_REQUEST

    user_object = user.findSingleUser({'email': email})
    error = Auth.login(user_object, password_hash)
    if error:
        return jsonify(LoggedIn=False, error=error), HTTP_400_BAD_REQUEST
    return user.get_basic_info_with_security(user_object)


@blueprint.route('/login-social', methods=['POST'])
def login_social():
    req = request.json
    try:
        social_type = req['socialType']
        token = req['token']
    except:
        return '', HTTP_400_BAD_REQUEST

    error = Auth.login_social(social_type, token)
    if error:
        return jsonify(LoggedIn=False, error=error), HTTP_400_BAD_REQUEST
    return user.get_basic_info_with_security(current_user)


@blueprint.route('/signup', methods=['POST'])
def signup():
    error = None
    req = request.json
    password = req['password']
    request_email = req['email'].lower()

    entry = user.findSingleUser({'email': request_email})

    if entry is None:
        try:
            invite_code = req['invite']
            if not invite.is_valid(invite_code):
                raise Exception("Invalid invite code")
            new_user = user.create_user(req)
            database_wrapper.save_entity(new_user)
            invite.consume(invite_code, new_user['_id'])
            print Auth.login(new_user, password), new_user, password
            #TODO: The issue is that get_basic_info_with_security which was
            #here before relies on the current_user field which is now not set
            #since there is no user logged in. Using the following method is a
            #temporary workaround.. Really a lot of this stuff needs refactoring
            #so I'm not going to write another get_basic_info method.
            basic_info = user.get_basic_info_from_users([new_user])[0]
        except Exception as e:
            return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
        #TODO:
        return jsonify(basic_info)
    else:
        error = 'Email is already in use'
        return jsonify(LoggedIn=False, error=error), HTTP_400_BAD_REQUEST


@blueprint.route('/logout', methods=['GET'])
@Auth.require(Auth.GHOST)
def logout():
    Auth.logout()
    return jsonify(LoggedIn=False, error=None)


@blueprint.route('/attach-social-login', methods=['POST'])
@Auth.require(Auth.GHOST)
def attach_social_login():
    req = request.json
    try:
        social_type = req['socialType']
        token = req['token']
    except:
        return '', HTTP_400_BAD_REQUEST

    SocialSignin.attach(current_user['_id'], social_type, token)
    return jsonify(error=None)
