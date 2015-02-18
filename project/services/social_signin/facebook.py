import urllib
import tornado.escape
from project.config import config

FACEBOOK_VALIDATE_SITE = 'https://graph.facebook.com'
FACEBOOK_VALIDATE_PATH = '/debug_token'


def verify(token):
    app_token = config['FB_SIGNIN_APPID'] + '|' + config['FB_SIGNIN_APPSECRET']
    params = urllib.urlencode({'access_token': app_token, 'input_token': token})
    url_query = FACEBOOK_VALIDATE_PATH + '?' + params
    request = urllib.urlopen(FACEBOOK_VALIDATE_SITE + url_query)
    text_response = request.read()
    response = tornado.escape.json_decode(text_response)
    try:
        if not response['data']['is_valid']:
            return None
    except:
        return None
    return response['data']['user_id']
