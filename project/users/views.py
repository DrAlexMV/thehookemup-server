from flask import flash, redirect, render_template, request, \
     url_for, Blueprint
from project.models import User, bcrypt
import time
from flask import request

users_blueprint = Blueprint(
    'users', __name__,
    template_folder='templates'
)

@users_blueprint.route("/")
def hello():
    return "Hello World!"


@users_blueprint.route('/login', methods=['GET', 'POST'])
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