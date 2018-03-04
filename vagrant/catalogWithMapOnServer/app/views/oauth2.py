import httplib2, json, requests
from .globalfile import getUserID, createOAuthUser

from .my_imports import Blueprint, request, flash, g, \
                        url_for, redirect, make_response, \
                        login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

oauth2 = Blueprint('oauth2', __name__)

# START FACEBOOK SIGN IN


@oauth2.route('/fbconnect', methods=['POST'])
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


@oauth2.route('/fbdisconnect')
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
        login_session.pop('state',None)
        clearLoginSession()
        del login_session['facebook_id']
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    return "You have been logged out"

# END FACEBOOK SIGN IN


@oauth2.route('/gconnect', methods=['POST'])
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


@oauth2.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        # print("Access Token is None")
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # print("In gdisconnect access token is %s" % access_token)
    # print("User name is: ")
    # print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # print("result is")
    # print(result)

    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['access_token']
        login_session.pop('state',None)
        clearLoginSession()
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@oauth2.route('/disconnect')
@oauth2.route('/logout')
def disconnect():
    isSessionValid = checkAccessToken()
    USER = g.user
    if ('provider' in login_session):
        if isSessionValid:
            if login_session['provider'] == 'google':
                gdisconnect()
            if login_session['provider'] == 'facebook':
                fbdisconnect()
            del login_session['provider']
            flash("You have successfully been logged out.")
        return redirect(url_for('catalog.landingPage'))
    elif USER:
        resp = make_response(redirect(url_for('catalog.landingPage')))
        del login_session['username']
        del login_session['user_id']        
        # logout(resp)
        flash("You have successfully been logged out.")
        return resp
    else:
        flash("You were not logged in")
        return redirect(url_for('catalog.landingPage'))

def checkAccessToken():
    """
    checkAccessToken:Check if the access token for OAuth login is valid of not
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
