import time
from flask import Flask,render_template,url_for,request,redirect,flash,jsonify, g
from models import Base, Item, UserProfile

from flask import make_response
from flask import session as login_session
import random,string

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import os, re
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
import logging


engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)



CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASSWORD_RE.match(password)

def verify_password(password,verify_password):
    return password == verify_password 

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email) 



@app.route('/')
@app.route('/home')
@app.route('/catalog')
def landingPage():
    #Below code show how to use HTML Template to achieve the same dynamically
    if('provider' in login_session and 'username' in login_session ):   
        return render_template('main.html',session=login_session,UserLogin=login_session['username'],LogoutSignup='logout',pagetitle='Home')
    else:
        return render_template('publicmain.html',session=login_session,UserLogin='login',LogoutSignup='signup',pagetitle='Home')    

@app.route('/catalog/<category>')
@app.route('/catalog/<category>/items')
def getCatalogItems(category):
    return render_template('items.html',session=login_session,UserLogin='login',LogoutSignup='signup',pagetitle='Items')

@app.route('/catalog/new',methods=['GET','POST'])
def newItem():
    return render_template('newitem.html',session=login_session,UserLogin='login',LogoutSignup='signup',pagetitle='New Items')
    
@app.route('/catalog/<item>/edit',methods=['GET','POST'])
def editItem(category):
    return render_template('edititem.html',session=login_session,UserLogin='login',LogoutSignup='signup',pagetitle='Edit Items')

@app.route('/catalog/<item>/delete',methods=['GET','POST'])
def deleteItem(category):
    return render_template('deleteitem.html',session=login_session,UserLogin='login',LogoutSignup='signup',pagetitle='Delete Items')

@app.route('/catalog.json')
def getCatalog():
    items = session.query(Item).all()
    #Populate an empty database
    if items :
        return jsonify(catalog = [i.serialize for i in items])

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
    # elif USER:
    #     resp = make_response(redirect(url_for('landingPage')))
    #     logout(resp)
    #     flash("You have successfully been logged out.")
    #     return resp
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
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.decode().split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
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
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
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
    output += ' " style = "width: 160px; height: 160px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

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

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)

    # url = 'https://graph.facebook.com/XXXXXX/permissions?access_token=EAAcPdwtESfUBAIImCgDZCGjFSxFsD6Y8TFkO3hNak9ZB566lxFohnaLQcM8ZCDvp3z6iRCvhmzmGZCdLeGRPFDYqRDIuBaNy7so9ADp1z7rOG0gxJPZA3x84k6ijx1QgTkZAojMbIYMm16zgtRrjEJWo9YMGs9ug8wYHDOuMv61QZDZD'
    
    h = httplib2.Http()
    result = h.request(url, 'DELETE')
    logging.warning('FB DELETE %s' % result[0])
    if result[0]['status'] == '200':
        clearLoginSession()
        del login_session['facebook_id']
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
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
    # check also if access token is valid or expired, if expired then resrore the access token
    stored_url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % stored_access_token)
    stored_h = httplib2.Http()
    stored_result = json.loads(stored_h.request(stored_url, 'GET')[1])
    
    if stored_access_token is not None and gplus_id == stored_gplus_id and stored_result.get('error') is None:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
        user_id=createOAuthUser(login_session)      
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 160px; height: 160px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print("Access Token is None")
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print("In gdisconnect access token is %s" % access_token)
    print("User name is: ")
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
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
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/login',methods=['GET','POST'])
def showLogin():
    if request.method == 'POST':        
        user_name = request.form['username']
        password = request.form['password']
        valid_user = False
        user = getUserByName(user_name)
        if user :
            valid_user = True
        if valid_user:      
            resp = make_response(redirect(url_for('landingPage')))            
            flash("You are now logged in as %s" % user_name)
            return resp
        else:   
            error  = "Invalid login"
            return render_template('login.html',error = error,UserLogin='login',LogoutSignup='signup',uname=user_name,pagetitle='login')                 

    else:    
        # USER = initialize()
        # if USER:
        #     return render_template('login.html',UserLogin=USER.user_name,LogoutSignup='logout',pagetitle='login')           
        # else:
            # Random string or rather salt 
            #state = ''.join(random.choice(string.letters) for x in xrange(32))   #--Python 2.x
        state = ''.join(random.choice(string.ascii_letters) for x in range(32))    #--Python 3.x
        login_session['state']=state
        #return "the current state is %s" % login_session['state']        
        return render_template('login.html',STATE=state,UserLogin='login',LogoutSignup='signup',pagetitle='login')

@app.route('/signup',methods=['GET','POST'])
def signUp():
    if request.method == 'POST':

        input_username = request.form['username']
        input_email = request.form['email']
        input_pw    = request.form['password']
        input_vpw   = request.form['verify']

        params = dict(uname=input_username,email=input_email)
        params['UserLogin'] = "login"
        params['LogoutSignup'] = "signup"        
        params['pagetitle'] = "Signup"        
        have_error = False

        username    = valid_username(input_username) 
        password    = valid_password(input_pw) 
        verify      = verify_password(input_pw,input_vpw) 
        email       = valid_email(input_email)

        unameerror  = None
        pwerror     = None
        vpwerror    = None
        emailerror  = None

        if not username:
            params['unameerror']  = "That's not a valid username."
            have_error = True 
        if not password:        
            params['pwerror']     = "That's not a valid password."
            have_error = True 
        elif not verify:        
            params['vpwerror']    = "Your passwords didn't match."
            have_error = True 
        if not email:
            params['emailerror']  = "That's not a valid email."
            have_error = True  

        if have_error:
            return render_template('signup.html',**params)
        else:
            user = getUserByName(input_username)
            user_id = getUserID(input_email)
            if user or user_id:
                params['unameerror']  = "That user already exists"
                return render_template('signup.html',**params)
            else:   
                user_id = signupUser(input_username,input_username,input_pw,input_email)
                resp = make_response(redirect(url_for('landingPage')))
                login(resp,str(user_id))
                return resp;
    else:
        kw = dict(UserLogin='login',LogoutSignup='signup',pagetitle='Signup')
        # USER = initialize()
        # if USER:
        #     kw['UserLogin']=USER.user_name
        #     kw['LogoutSignup']='logout'
        return render_template('signup.html',**kw)    

def getUserByName(username):
    try:
        user = session.query(UserProfile).filter_by(username=username).one()
        return user
    except Exception as e:
        return None

def getUserID(email):
    try:
        user = session.query(UserProfile).filter_by(email=email).one()
        return user.id  
    except Exception as e:
        return None

def createOAuthUser(login_session):
    newUser = UserProfile(username=login_session['username'],email=login_session['email'],picture=login_session['picture'],oauth_user='yes')
    session.add(newUser)
    session.commit()
    user = session.query(UserProfile).filter_by(email=login_session['email']).one()
    return user.id

def signupUser(name,username,pw,email):
    hash_pw = '1234'   
    newUser = UserProfile(username=username,password_hash=hash_pw,email=email,oauth_user='no')
    session.add(newUser)
    session.commit()    
    return user.id

def checkAccessToken():
    stored_access_token = login_session.get('access_token')
    result={}
    if stored_access_token:
        h = httplib2.Http()
        if login_session.get('gplus_id') is not None:
            url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
                   % stored_access_token)
            result = json.loads(h.request(url, 'GET')[1])
        if login_session.get('facebook_id') is not None:
            url = ('https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' 
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
    del login_session['user_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']    

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # PORT = int(os.environ.get('PORT'))
    PORT = 8000
    app.run(host='0.0.0.0',port=PORT)