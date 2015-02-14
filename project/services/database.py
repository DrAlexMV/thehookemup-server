import mongokit


class Database:
    def __init__(self):
        self.__connection = None
        self.config = {}

    def connect(self, config):
        print 'Connecting to mongodb at: %s %i' % (config['MONGODB_HOST'], config['MONGODB_PORT'])
        self.__connection = mongokit.Connection(config['MONGODB_HOST'], config['MONGODB_PORT'])
        self.config = config

    def __getitem__(self, db_name):
        return self.__connection[self.config['DATABASE_NAME']][db_name]

    def connection(self):
        return self.__connection

# singleton (soft enforcement)
Database = Database()
