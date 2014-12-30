from flask import Flask
from mongokit import Connection, Document
from flask import request
import time
from flask import request

from flask.ext.cors import CORS

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# create the little application object
app = Flask(__name__)
cors = CORS(app)

app.config.from_object(__name__)
app.config['DEBUG'] = True

# connect to the database
connection = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

class User(Document):
    structure = {
        'name': unicode,
        'email': unicode,
        'password': unicode
    }
    validators = {
        'name': max_length(50),
        'email': max_length(120)
        'password': max_length(120)
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.name)

# register the User document with our current connection
connection.register([User])

@app.route("/")
def hello():
    return "Hello World!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(name=request.form['username']).first()
        if user is not None and bcrypt.check_password_hash(
            user.password, request.form['password']
        ):
            login_user(user)
            today = time.strftime("%c")
            user.last_login_dt=today
            flash('You were logged in. Go Crazy.')
            if user.admin==True:
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('home.home'))

        else:
            error = 'Invalid username or password.'
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run()
    flash('hello world')


