from app import Location, Item, UserProfile, \
                        Blueprint, render_template, \
                        jsonify, g, func, login_session, \
                        request
from .globalfile import session, login_required


from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

apis = Blueprint('apis', __name__)


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
    print "\n***Parameters to verify_password***"
    print "username_or_token : %s" % username_or_token
    print "password : %s" % password
    print "\n***Flask Session Object***"
    print login_session
    print "\n***Request Header***"
    print request.headers
    print request.authorization
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

@apis.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@apis.route('/catalog.json')
@auth.login_required
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

@apis.route('/location.json')
def locationJSON():
    locations = session.query(Location).all()
    listLocations=[]
    j=0
    for i in locations:
        if i.serializeLocations !=[]:
            listLocations.append(i.serializeLocations)
        j=j+1
    response = jsonify(Places=listLocations)
    return response    
