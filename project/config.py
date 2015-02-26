import os
import json

config = {}

# Defaults
config['HOST'] = ''
config['PORT'] = 5000
config['MONGODB_HOST'] = 'localhost'
config['MONGODB_PORT'] = 27017
config['ELASTIC_HOST'] = 'localhost'
config['ELASTIC_PORT'] = 9200
config['ACCEPTED_ORIGINS'] = ['http://localhost:3000']
config['DEBUG'] = False
config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
config['DATABASE_NAME'] = 'thehookemup'
config['ROUTE_PREPEND'] = '/api/v1'
config['FB_SIGNIN_APPID'] = '744792018972866'
config['FB_SIGNIN_APPSECRET'] = 'd12045378fed762da38f9a882f727828'

config['ENABLE_ACCOUNT_APPROVALS'] = True
config['NEW_USER_INVITE_NUM'] = 3
config['INVITE_CODE_LENGTH'] = 10

# Load config file if there is one
config_file = os.environ.get('CONFIG_FILE')
if config_file:
    print "Loading config from %s" % config_file
    file_customization = json.load(open(config_file))
    config.update(file_customization)

# Load environment variable settings
# List of environment variable aliases mapped to their config settings
environment_vars_configs = {'API_PORT': 'PORT', 'DB_NAME': 'DATABASE_NAME', 'MONGODB_PORT_27017_TCP_ADDR': 'MONGODB_HOST', 'ELASTIC_PORT_9300_TCP_ADDR': 'ELASTIC_HOST'}
for env_key, config_name in environment_vars_configs.items():
    env_value = os.environ.get(env_key)
    if env_value is not None:
        config[config_name] = env_value
