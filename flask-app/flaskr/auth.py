from flask import Blueprint, render_template, redirect, \
    url_for, request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from .models import Subscriber, Professional
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # if already logged in, skip the login page
    if session.get('user_id'):
        return redirect(url_for('home'))

    active_tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        if request.form.get('form_type') == 'register':
            # handle register post
            # call the register function
            return register()

        email = request.form.get('email')
        password = request.form.get('password')

        # query the database for emails as they must be unique
        user = Subscriber.query.filter_by(email=email).first()

        # check password hash using library
        if user and check_password_hash(user.pswd_hash, password):
            session['user_id'] = user.subscriber_id
            flash('Login successful', 'success')
            # send logged in user to home page
            return redirect(url_for('home'))

        # if not found in subscribers
        # check professionals (professionals can log in with same form)
        if not user:
            user = Professional.query.filter_by(email=email).first()

        if user and check_password_hash(user.pswd_hash, password):
            session['user_id'] = user.professional_id
            # set a flag in the session to indicate this is a professional user
            session['is_professional'] = True
            flash('Login successful as professional', 'success')
            # send logged in user to home page
            return redirect(url_for('home'))

        # if login fails, show error and stay on login page
        flash('Invalid email or password')

    # show the auth page for failed logins
    return render_template('auth.html', active_tab=active_tab)


# If user is logged in already
# redirect them to home otherwise show login page
@auth_bp.route('/auth')
def auth_page():
    if session.get('user_id'):
        return redirect(url_for('home'))

    tab = request.args.get('tab', 'login')
    return render_template('auth.html', active_tab=tab)


# allow new users to register
@auth_bp.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    address = request.form.get('address')
    gender = request.form.get('gender')
    dob_str = request.form.get('date_of_birth')
    is_professional = request.form.get('is_professional') == 'true'

    # email is correct format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # validate all fields are present
    if not email or not password\
            or not confirm_password\
            or not address\
            or not gender\
            or not dob_str\
            or not name:
        flash('All registration fields are required.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # validates passwords match
    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # Ensures email is unique
    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        flash('Email already registered', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # checks date of birth is valid format and converts to date object
    try:
        date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Date of birth must be in YYYY-MM-DD format.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # hashes password for storage
    password_hash = generate_password_hash(password)

    # block professional signup until workflow is implemented
    print(is_professional)
    if is_professional:
        new_user = Professional.create_new_professional(
            email=email,
            name=name,
            address=address,
            pswd_hash=password_hash,
            profession=None
        )
        session['user_id'] = new_user.professional_id
        # set a flag in the session to indicate user is professional
        session['is_professional'] = True

    else:
        # creates new user in database
        new_user = Subscriber.create_new_subscriber(
            email=email,
            name=name,
            address=address,
            pswd_hash=password_hash,
            sex=gender,
            date_of_birth=date_of_birth,
            height=None,
            weight=None
        )

        # logs new user in and redirects to home page
        session['user_id'] = new_user.subscriber_id
    flash('Registration successful, you are now logged in', 'success')
    return redirect(url_for('dashboard'))


# logs user out by clearing session and redirecting to login page
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
