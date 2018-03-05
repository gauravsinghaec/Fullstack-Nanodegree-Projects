from flask import Flask
import random, string
from .utils import valid_username, valid_password, match_password, \
            valid_email
from flask import g, redirect, url_for, request, jsonify, \
                Blueprint, render_template, flash, \
                make_response
from flask import session as login_session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models.item import Item
from .models.location import Location
from .models.user import Base, UserProfile
from functools import wraps

from views.oauth2 import oauth2
from views.usermap import usermap
from views.apis import apis
from views.home import home
from views.catalog import catalog

from views.globalfile import getUserById

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
