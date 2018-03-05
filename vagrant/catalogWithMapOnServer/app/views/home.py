from app import Blueprint, render_template, url_for, \
                        request, flash, login_session, \
                        random, string, make_response, \
                        valid_username, valid_password, \
                        match_password, valid_email
from .globalfile import redirect_dest                        
from .globalfile import session, login_required, ownership_required, \
                        getUserById, signupUser, getUserByName, getUserID

home = Blueprint('home', __name__)

@home.route('/contact')
def contact():
    # g.kwargs['pagetitle'] = 'Contact us'
    pagetitle = 'Contact us'
    return render_template('contact.html', pagetitle= pagetitle)

@home.route('/about')
def about():
    # g.kwargs['pagetitle'] = 'About'
    pagetitle = 'About'
    return render_template('about.html', pagetitle= pagetitle )

@home.route('/')
@home.route('/login', methods=['GET', 'POST'])
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
            resp = make_response(redirect_dest(fallback=url_for('catalog.landingPage')))
            flash("You are now logged in as %s" % user_name)
            return resp
        else:
            error = "Invalid login"
            return render_template('home/login.html', error=error,
                                   uname=user_name, pagetitle='login')

    else:
        state = ''.join(random.choice(string.ascii_letters)
                        for x in range(32))  # --Python 3.x
        login_session['state'] = state
        return render_template('home/login.html', STATE=state, pagetitle='login')


@home.route('/signup', methods=['GET', 'POST'])
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
            return render_template('home/signup.html', **params)
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
                return render_template('home/signup.html', **params)
            else:
                user_id = signupUser(input_username, input_pw, input_email)
                login_session['username'] = input_username
                login_session['user_id'] = user_id
                resp = make_response(redirect(url_for('catalog.landingPage')))
                return resp
    else:
        kw = dict(pagetitle='Signup')
        return render_template('home/signup.html', **kw)
