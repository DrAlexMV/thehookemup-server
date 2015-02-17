from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado import autoreload
from project import app, config
import sys

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(config['PORT'])
ioloop = IOLoop.instance()

if len(sys.argv) > 1 and sys.argv[1] == 'development':
    print 'The server is running in development mode.'
    autoreload.start(ioloop)

ioloop.start()
