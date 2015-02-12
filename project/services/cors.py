from flask.ext.cors import CORS

class Cors:
	def __init__(self):
		self.cors = None

	def init_app(self, app, config):
		# keeping the cors instance may not matter.
		self.cors = CORS(app, allow_headers=['Origin','Content-Type', 'Cache-Control', 'X-Requested-With'],
			supports_credentials=True,
			origins=config['ACCEPTED_ORIGINS'])

Cors = Cors()
