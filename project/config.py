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
config['ACCEPTED_ORIGINS'] = ['http://104.236.77.225', 'http://localhost:3000']
