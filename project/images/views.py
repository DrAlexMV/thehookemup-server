from flask import redirect, render_template, request, \
    url_for, Blueprint, request, jsonify, session, Response, make_response
from flask.ext.login import login_required
from project import bcrypt, ROUTE_PREPEND, utils
from flask.ext.api import FlaskAPI, exceptions
from flask.ext.api.status import *
from bson.objectid import ObjectId
from wand.image import Image
from werkzeug import secure_filename
from models.user import getUserID
from models.image import create_image, find_image_by_id

ALLOWED_EXTENSIONS = set(['bmp', 'png', 'jpg', 'jpeg', 'gif'])

PROFILE_SIZE = 280 #280 x 280px
PROFILE_FORMAT = 'jpeg'
PROFILE_QUALITY = 85

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

images_blueprint = Blueprint(
    'images', __name__
)

def crop_image(image):
    crop = image.clone()
    square_size = min(crop.height, crop.width)
    crop.transform('%ix%i'%(square_size, square_size),
        '%ix%i'%(PROFILE_SIZE, PROFILE_SIZE))
    crop.format = PROFILE_FORMAT
    crop.compression_quality = PROFILE_QUALITY
    return crop

@images_blueprint.route(ROUTE_PREPEND+'/image', methods=['POST'])
@login_required
def upload_image():
    request_error = ''
    user_id = getUserID('me')
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            image_blob = crop_image(Image(file=file)).make_blob()
            image_id = create_image(image_blob, user_id)
            return jsonify(error=None, imageID=str(image_id) + '.' + PROFILE_FORMAT)
        except Exception as e:
            request_error = str(e)
    return jsonify(error=request_error), HTTP_400_BAD_REQUEST

@images_blueprint.route(ROUTE_PREPEND+'/image/<imageid>.jpg', methods=['GET'])
@login_required
def get_image(imageid):
    entry = find_image_by_id(imageid)
    if entry is None:
        return '', HTTP_404_NOT_FOUND

    response = make_response(entry['data'])
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@images_blueprint.route(ROUTE_PREPEND+'/image/<imageid>.jpg', methods=['DELETE'])
@login_required
def delete_image(imageid):
    entry = find_image_by_id(imageid)
    if entry is None:
        return '', HTTP_404_NOT_FOUND

    if entry['owner'] != getUserID('me'): # TODO: Add admin override
        return '', HTTP_401_NOT_AUTHORIZED

    entry.delete()
    return '', HTTP_200_OK
