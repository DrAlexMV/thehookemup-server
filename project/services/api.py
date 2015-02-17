import flask


class API:
    api_modules = ['users', 'account', 'images', 'search', 'startups', 'invites', 'endorsements', 'admins']

    def __init__(self):
        self.blueprints = []

    def configure(self, config):
        self.config = config

    def register_blueprints(self, app, config):
        added_blueprints = map(lambda module_name: self.register_blueprint(app, module_name), self.api_modules)

    def register_blueprint(self, app, module_name):
        mod = __import__('project.api.' + module_name, fromlist=['blueprint'])
        app.register_blueprint(mod.blueprint, url_prefix=self.config['ROUTE_PREPEND'])
        self.blueprints.append(mod.blueprint)
        return mod.blueprint

API = API()
