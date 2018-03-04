import random, string
from app.utils import valid_username, valid_password, match_password, \
			valid_email
from flask import g, redirect, url_for, request, jsonify, \
				Blueprint, render_template, flash, \
				make_response
from flask import session as login_session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.item import Item
from app.models.location import Location
from app.models.user import Base, UserProfile
from functools import wraps


