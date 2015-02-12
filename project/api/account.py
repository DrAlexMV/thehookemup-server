from flask import request, jsonify, Blueprint
from project.services.auth import Auth
from models import user
from flask_api.status import HTTP_400_BAD_REQUEST
from bson.json_util import dumps

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
        return jsonify(LoggedIn=False, error=error),HTTP_400_BAD_REQUEST
    return user.get_basic_info_with_security(user_object)

@blueprint.route('/signup', methods=['POST'])
def signup():
    #TODO: comment in lines to enforce invite codes
    error = None
    req = request.json
    request_email = req['email'].lower()
    print request_email
    entry = user.findSingleUser({'email': request_email})
    print entry
    if entry is None:
        try:
            #invite_code = req['inviteCode']
            new_user = user.create_user(req)
            database_wrapper.save_entity(new_user)
            #invite.consumeInvite(ObjectId(invite_code), str(new_user._id))
        except Exception as e:
            return jsonify(error=str(e)), HTTP_400_BAD_REQUEST
        Auth.login(new_user, new_user['password'])
        return user.get_basic_info_with_security(new_user)
    else:
        error = 'Email is already in use'
        return jsonify(LoggedIn=False, error=error), HTTP_400_BAD_REQUEST


@blueprint.route('/logout', methods=['GET'])
@Auth.require(Auth.GHOST)
def logout():
    Auth.logout()
    return jsonify(LoggedIn=False, error=None)
