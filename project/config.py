import os

config = {}

system_mongo_host = os.environ.get('MONGODB_PORT_27017_TCP_ADDR')
system_elastic_host = os.environ.get('ELASTIC_PORT_9300_TCP_ADDR')

config['HOST'] = ''
config['PORT'] = 5000
config['MONGODB_HOST'] = system_mongo_host if system_mongo_host else 'localhost'
config['MONGODB_PORT'] = 27017
config['ELASTIC_HOST'] = system_elastic_host if system_elastic_host else 'localhost'
config['ELASTIC_PORT'] = 9200
config['ACCEPTED_ORIGINS'] = ['http://beta.founderati.io', 'http://beta.thehookemup.com', 'http://104.236.77.225', 'http://localhost:3000', 'http://104.236.196.182']
config['DEBUG'] = False
config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
config['DATABASE_NAME'] = 'thehookemup'
config['ROUTE_PREPEND'] = '/api/v1'
config['FB_SIGNIN_APPID'] = '744792018972866'
config['FB_SIGNIN_APPSECRET'] = 'd12045378fed762da38f9a882f727828'

config['NEW_USER_INVITE_NUM'] = 3
