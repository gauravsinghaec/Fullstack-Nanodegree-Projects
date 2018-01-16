import time
from flask import Flask, render_template, url_for, request, redirect, flash

from models import Base, Item, UserProfile

from flask import make_response, jsonify, g
from flask import session as login_session
import random
import string

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func
import os
import re
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
import logging

from functools import wraps

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    """
    valid_username: Regex to validate username
    Args:
        username (data type: str): username
    Returns:
        return boolean True/False
    """
    return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    """
    valid_password: Regex to validate password
    Args:
        password (data type: str): password
    Returns:
        return boolean True/False
    """
    return password and PASSWORD_RE.match(password)


def match_password(password, verify_password):
    """
    match_password: function to confirm retyping password is same
    Args:
        password (data type: str): password
        verify_password (data type: str): retype password
    Returns:
        return boolean True/False
    """
    return password == verify_password

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_email(email):
    """
    valid_username: Regex to validate email
    Args:
        email (data type: str): email
    Returns:
        return boolean True/False
    """
    return not email or EMAIL_RE.match(email)


# ADD @auth.verify_password decorator here
@auth.verify_password
def verify_password(username_or_token, password):
    """
    verify_password: @auth.verify_password decorator to validate login usen
    Args:
        username_or_token (data type: str): username or access_token
        password (data type: str): password
    Returns:
        return boolean True/False
    """
    # check if the token is provided as username
    print "username_or_token : %s" % username_or_token
    print "password : %s" % password
    user_id = UserProfile.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(UserProfile).filter_by(id=user_id).one()
    else:
        user = session.query(UserProfile).filter_by(
            username=username_or_token).first()
        if not user:
            print "User Not Found"
            return False
        elif not user.verify_password(password):
            print "Unable to verify password"
            return False
    if user:
        g.user = user
        return True
    print "User Not Found"
    return False

# add /token route here to get a token for a user with login credentials


def login_required(f):
    """
    A function decorator to avoid that code repetition
    fo checking user login status
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


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


# def ownership_required(f):
#     """
#     A function decorator to avoid unauthorized CRUD
#     """
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         item = session.query(Item).filter_by(id=item_id).one()
#         if item.user_id != login_session['user_id']:
#             flash('unauthorized access: Only the onwer can edit/delete item')
#             return redirect(url_for('showLogin', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/')
@app.route('/catalog')
def landingPage():
    items = session.query(Item).order_by('last_updated desc').all()
    categories = session.query(Item.category, func.count(
        Item.category)).group_by(Item.category).all()

    # Below code show how to use HTML Template to achieve the same dynamically
    if('username' in login_session and checkAccessToken()):
        return render_template('main.html',
                               session=login_session,
                               items=items,
                               categories=categories,
                               pagetitle='Home')
    else:
        return render_template('publicmain.html',
                               session=login_session,
                               items=items,
                               categories=categories,
                               pagetitle='Home')


@app.route('/catalog/<category>')
@app.route('/catalog/<category>/items')
def getCatalogItems(category):
    categories = session.query(Item.category, func.count(
        Item.category)).group_by(Item.category).all()
    items = session.query(Item).filter_by(
        category=category).order_by('last_updated desc').all()
    if items != []:
        return render_template('items.html', session=login_session,
                               items=items, categories=categories,
                               pagetitle='Items')
    else:
        return redirect(url_for('landingPage'))


@app.route('/catalog/<category>/<itemname>')
def getCatalogItemDetails(category, itemname):
    item = session.query(Item).filter_by(
        category=category, title=itemname).one()
    itemCreator = getUserById(item.user_id)
    if ('username' not in login_session or
            itemCreator.id != login_session['user_id']):
        return render_template('publicitemdetail.html', session=login_session,
                               item=item, category=category,
                               pagetitle='Items')
    return render_template('itemdetail.html', session=login_session,
                           item=item, category=category,
                           pagetitle='Items')


@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
    	if checkDuplicateItem(request.form['title'],request.form['category']):
    		flash('Item already exists under the selected category')	
        	return render_template('newitem.html',
        	                   session=login_session, pagetitle='New Items')
        createItem(request.form['title'], request.form['description'],
                   request.form['category'], login_session['user_id'])
        flash('New item created')
        return redirect(url_for('getCatalogItems',
                                category=request.form['category']))
    else:
        return render_template('newitem.html',
                               session=login_session, pagetitle='New Items')


@app.route('/catalog/<int:item_id>/<itemname>/edit', methods=['GET', 'POST'])
@login_required
# @ownership_required
def editItem(item_id, itemname):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if item.user_id != g.user.id:
        flash('unauthorized access: Only the onwer can edit/delete items')
        return redirect(url_for('showLogin', next=request.url))
    if request.method == 'POST':
        if item != []:
            fields = {}
            fields['title'] = request.form['title']
            fields['description'] = request.form['description']
            fields['category'] = request.form['category']
            if checkDuplicateItem(fields['title'],fields['category']):
            	flash('Item already exists under the selected category')	
            	return render_template('edititem.html',session=login_session,
            	                   item=item, pagetitle='Edit Items')            
            updateItem(item=item, **fields)
            flash('Item "' + item.title + '" updated successfully')
        return redirect(url_for('getCatalogItems',
                                category=fields['category']))
    else:
        return render_template('edititem.html', session=login_session,
                               item=item, pagetitle='Edit Items')


@app.route('/catalog/<int:item_id>/<itemname>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(item_id, itemname):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    if item.user_id != g.user.id:
        flash('unauthorized access: Only the onwer can edit/delete items')
        return redirect(url_for('showLogin', next=request.url))
    if request.method == 'POST':
        if item != []:
            removeItem(item=item)
            flash('Item "' + item.title + '" deleted successfully')
        return redirect(url_for('getCatalogItems', category=item.category))
    else:
        return render_template('deleteitem.html', session=login_session,
                               item=item, pagetitle='Delete Items')


@app.route('/catalog.json')
@login_required
def getCatalog():
    categories = session.query(Item.category, func.count(
        Item.category)).group_by(Item.category).all()
    Category = []
    if categories:
        for cat in categories:
            items = session.query(Item).filter_by(category=cat.category).all()
            Category.append(
                {'Item': [i.serialize for i in items], 'name': cat.category})
    return jsonify(Category=Category)


@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        valid_user = False
        user = getUserByName(user_name)
        if user and user.verify_password(password):
            valid_user = True
        if valid_user:
            login_session['username'] = user_name
            login_session['user_id'] = user.id
            resp = make_response(redirect(url_for('landingPage')))
            flash("You are now logged in as %s" % user_name)
            return resp
        else:
            error = "Invalid login"
            return render_template('login.html', error=error,
                                   uname=user_name, pagetitle='login')

    else:
        state = ''.join(random.choice(string.ascii_letters)
                        for x in range(32))  # --Python 3.x
        login_session['state'] = state
        return render_template('login.html', STATE=state, pagetitle='login')


@app.route('/signup', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':

        input_username = request.form['username']
        input_email = request.form['email']
        input_pw = request.form['password']
        input_vpw = request.form['verify']

        params = dict(uname=input_username, email=input_email)
        params['UserLogin'] = "login"
        params['LogoutSignup'] = "signup"
        params['pagetitle'] = "Signup"
        have_error = False

        username = valid_username(input_username)
        password = valid_password(input_pw)
        verify = match_password(input_pw, input_vpw)
        email = valid_email(input_email)

        unameerror = None
        pwerror = None
        vpwerror = None
        emailerror = None

        if not username:
            params['unameerror'] = "That's not a valid username."
            have_error = True
        if not password:
            params['pwerror'] = "That's not a valid password."
            have_error = True
        elif not verify:
            params['vpwerror'] = "Your passwords didn't match."
            have_error = True
        if not email:
            params['emailerror'] = "That's not a valid email."
            have_error = True

        if have_error:
            return render_template('signup.html', **params)
        else:
            user_exists = False
            user = getUserByName(input_username)
            if user:
                params['unameerror'] = "That user already exists"
                user_exists = True
            if (input_email and getUserID(input_email)):
                params['emailerror'] = "Email already exists"
                user_exists = True

            if user_exists:
                return render_template('signup.html', **params)
            else:
                user_id = signupUser(input_username, input_pw, input_email)
                login_session['username'] = input_username
                login_session['user_id'] = user_id
                resp = make_response(redirect(url_for('landingPage')))
                return resp
    else:
        kw = dict(pagetitle='Signup')
        return render_template('signup.html', **kw)


@app.route('/disconnect')
@app.route('/logout')
def disconnect():
    isSessionValid = checkAccessToken()
    # USER = initialize()
    if ('provider' in login_session):
        if isSessionValid:
            if login_session['provider'] == 'google':
                gdisconnect()
            if login_session['provider'] == 'facebook':
                fbdisconnect()
            del login_session['provider']
            flash("You have successfully been logged out.")
        return redirect(url_for('landingPage'))
    elif ('username' in login_session):
        resp = make_response(redirect(url_for('landingPage')))
        del login_session['username']
        del login_session['user_id']
        flash("You have successfully been logged out.")
        return resp
    else:
        flash("You were not logged in")
        return redirect(url_for('landingPage'))

# START FACEBOOK SIGN IN


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode()
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?' +
           'grant_type=fb_exchange_token' +
           '&client_id=%s&client_secret=%s&fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange,
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.decode().split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?' +
           'access_token=%s&fields=name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print("url sent for API access:%s"% url)
    # print("API JSON result: %s" % result)
    data = json.loads(result.decode())
    logging.error(data)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?' +
           'access_token=%s&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode())

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createOAuthUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 160px; height: 160px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("You are now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    # Only disconnect a connected user.
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)

    h = httplib2.Http()
    result = h.request(url, 'DELETE')
    logging.warning('FB DELETE %s' % result[0])
    if result[0]['status'] == '200':
        clearLoginSession()
        del login_session['facebook_id']
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    return "You have been logged out"

# END FACEBOOK SIGN IN


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # check also if access token is valid or expired, if expired then resrore
    # the access token
    stored_url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % stored_access_token)
    stored_h = httplib2.Http()
    stored_result = json.loads(stored_h.request(stored_url, 'GET')[1])

    if (stored_access_token is not None and gplus_id == stored_gplus_id and
            stored_result.get('error') is None):
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createOAuthUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 160px; height: 160px;border-radius: 150px;\
    -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print("Access Token is None")
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("In gdisconnect access token is %s" % access_token)
    print("User name is: ")
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print("result is")
    print(result)

    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['access_token']
        clearLoginSession()
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def checkDuplicateItem(title,category):
    """
    checkDuplicateItem: This function checks item existense
    Args:
        title (data type: str): item's title
        category (data type: str): item's category
    Returns:
        return true/false
    """
    item = session.query(Item).filter_by(
        category=category, title=title).one_or_none()	
    if item:
    	return True
    return False	

def createItem(title, description, category, user_id):
    """
    createItem: This function creates the catalog item with given values
    Args:
        title (data type: str): item's title
        description (data type: str): item's description
        category (data type: str): item's category
        user_id (data type: int): user who is creating the item
    Returns:
        no return value
    """

    newItem = Item(title=title, description=description,
                   category=category, user_id=user_id)
    session.add(newItem)
    session.commit()
    return


def updateItem(item, **fields):
    """
    updateItem: This function update the given catalog item with updated values
    Args:
        item (data type: dictionary): item object
        **fields (data type: dictionary): key:values paired object
    Returns:
        no return value
    """
    item.title = fields['title']
    item.description = fields['description']
    item.category = fields['category']
    session.add(item)
    session.commit()
    return


def removeItem(item):
    """
    removeItem: This function removes the catalog item from database
    Args:
        item (data type: dictionary): item object
    Returns:
        no return value
    """
    session.delete(item)
    session.commit()


def getUserByName(username):
    """
    getUserById: this function finds user if the username is valid
    Args:
        username (data type: str): Unique username
    Returns:
        return user object if found otherwiese None
    """
    try:
        user = session.query(UserProfile).filter_by(username=username).one()
        return user
    except Exception as e:
        return None


def getUserById(user_id):
    """
    getUserById: this function finds user if the user_id is valid
    Args:
        user_id (data type: int): Unique user ID
    Returns:
        return user object if found otherwiese None
    """
    try:
        user = session.query(UserProfile).filter_by(id=user_id).one()
        return user
    except Exception as e:
        return None


def getUserID(email):
    """
    getUserID: this function finds user if the email is registered
    Args:
        email (data type: str): user's email
    Returns:
        return unique user_id if found otherwiese None
    """
    try:
        user = session.query(UserProfile).filter_by(email=email).one()
        return user.id
    except Exception as e:
        return None


def createOAuthUser(login_session):
    """
    createOAuthUser: This function creates new user in database on
    first time OAuth login
    Args:
        login_session(data type: dictionary): this object has user OAuth detail
    Returns:
        returns unique user_id on successfull oauth login
    """
    newUser = UserProfile(username=login_session['username'],
                          email=login_session['email'],
                          picture=login_session['picture'],
                          oauth_user='yes')
    session.add(newUser)
    session.commit()
    user = session.query(UserProfile).filter_by(
        email=login_session['email']).one()
    return user.id


def signupUser(username, pw, email):
    """
    signupUser: This function creates new user in database on signup
    Args:
        username (data type: str): input username
        password (data type: str): input password
        email (data type: str): input email
    Returns:
        returns unique user_id on successfull signup
    """
    password = pw
    newUser = UserProfile(username=username, email=email, oauth_user='no')
    newUser.hash_password(password)
    session.add(newUser)
    session.commit()
    return newUser.id


def checkAccessToken():
    """
    checkAccessToken: Check if the access token for OAuth login is valid of not
    Args:
        no argument needed
    Returns:
        returns boolean True/False
    """

    stored_access_token = login_session.get('access_token')
    result = {}
    if stored_access_token:
        h = httplib2.Http()
        if login_session.get('gplus_id') is not None:
            url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?' +
                   'access_token=%s' % stored_access_token)
            result = json.loads(h.request(url, 'GET')[1])
        if login_session.get('facebook_id') is not None:
            url = ('https://graph.facebook.com/v2.8/me?' +
                   'access_token=%s&fields=name,id,email'
                   % stored_access_token)
            result = json.loads(h.request(url, 'GET')[1].decode())
        if result.get('error') is not None:
            flash('Seesion expired- You are being logged out')
            if login_session.get('gplus_id'):
                del login_session['gplus_id']
            if login_session.get('facebook_id'):
                del login_session['facebook_id']
            del login_session['access_token']
            clearLoginSession()
            return False
    return True


def clearLoginSession():
    """
    clearLoginSession: this function is used to clear the session elements
    Args:
        no argument needed
    Returns:
        no return value
    """
    del login_session['user_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # PORT = int(os.environ.get('PORT'))
    PORT = 8000
    app.run(host='0.0.0.0', port=PORT)
