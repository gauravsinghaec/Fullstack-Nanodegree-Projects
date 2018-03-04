from flask import Flask
from views.oauth2 import oauth2
from views.usermap import usermap
from views.apis import apis
from views.home import home
from views.globalfile import login_required, ownership_required
from views.catalog import catalog

from views.globalfile import getUserById
from views.my_imports import login_session, g

app = Flask(__name__)
app.register_blueprint(oauth2)
app.register_blueprint(usermap)
app.register_blueprint(apis)
app.register_blueprint(home)
app.register_blueprint(catalog, url_prefix='/catalog')

@app.before_request
def before_request():
    """
    Any functions that are decorated with before_request will run
    before the view function each time a request is received
    """
    g.user = None

    # pull user info from the database based on login_session id
    # this will set flask variable g and will be used in login_required def
    # above
    if 'user_id' in login_session:
        try:
            try:
                g.user = getUserById(login_session['user_id'])
            except TypeError:  # session probably expired
                pass
        except KeyError:
            pass
