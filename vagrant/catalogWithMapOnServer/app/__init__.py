from flask import Flask
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from functools import wraps

# Define the WSGI application object
app = Flask(__name__)

# Configurations 
app.config.from_object('config')

# Define a base model for other database tables to inherit
Base = declarative_base()

# Define db session object which is imported
# by modules and controllers
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


import random, string
from .utils import valid_username, valid_password, match_password, \
            valid_email
from flask import g, redirect, url_for, request, jsonify, \
                Blueprint, render_template, flash, \
                make_response
from flask import session as login_session
from .models.item import Item
from .models.location import Location
from .models.user import Base, UserProfile

from views.oauth2 import oauth2
from views.usermap import usermap
from views.apis import apis
from views.home import home
from views.catalog import catalog

app.register_blueprint(oauth2)
app.register_blueprint(usermap)
app.register_blueprint(apis)
app.register_blueprint(home)
app.register_blueprint(catalog, url_prefix='/catalog')
