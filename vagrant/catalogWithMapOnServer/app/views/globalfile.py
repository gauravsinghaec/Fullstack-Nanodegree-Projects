from .my_imports import g, redirect, url_for, request, \
                        login_session, wraps, \
                        Item, Base, UserProfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def redirect_dest(fallback):
    dest = request.args.get('next')
    if dest:
        return redirect(dest)
    else:
        return redirect(fallback)


def login_required(f):
    """
    A function decorator to avoid that code repetition
    fo checking user login status
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('home.showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def ownership_required(f):
    """
    A function decorator to avoid unauthorized CRUD
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        item_id = kwargs['item_id']
        item = session.query(Item).filter_by(id=item_id).one()
        if item.user_id != login_session['user_id']:
            flash('unauthorized access: Only the onwer can edit/delete item')
            return redirect(url_for('home.showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


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
