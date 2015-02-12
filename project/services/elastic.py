from elasticsearch import Elasticsearch
from project import init_elastic

class Elastic:
	def __init__(self):
		self.__connection = None
		self.config = {}

	def connect(self, config):
		print 'Connecting to elastic search at: %s %i' % (config['ELASTIC_HOST'], config['ELASTIC_PORT'])
		self.__connection = Elasticsearch([config['ELASTIC_HOST']], port=config['ELASTIC_PORT'])
		self.config = config

		# update structure if needed
		self.init_indices()

	def init_indices(self):
		init_elastic.generate_search_structure(self.__connection)

	def connection(self):
		return self.__connection

# singleton (soft enforcement)
Elastic = Elastic()
