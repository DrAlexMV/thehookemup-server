from project import app
from project.config import config

if __name__ == '__main__':
    app.run(host=config['HOST'], port=config['PORT'], debug=config['DEBUG'])
