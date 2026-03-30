from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from .models import Subscriber  # Assuming you have a User model in models.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, skip the login page
    if session.get('user_id'):
        return redirect(url_for('home'))

    active_tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        if request.form.get('form_type') == 'register':
            # handle register post (currently placeholder)
            register()  # Call the register function to handle registration

        email = request.form.get('email')
        password = request.form.get('password')

        # Query the database
        user = Subscriber.query.filter_by(email=email).first()

        # Check password hash
        if user and check_password_hash(user.pswd_hash, password):
            session['user_id'] = user.subscriber_id
            return redirect(url_for('home'))

        flash('Invalid email or password')

    # Show the auth page for GET requests or failed logins
    return render_template('auth.html', active_tab=active_tab)

@auth_bp.route('/auth')
def auth_page():
    if session.get('user_id'):
        return redirect(url_for('home'))

    tab = request.args.get('tab', 'login')
    return render_template('auth.html', active_tab=tab)

@auth_bp.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    address = request.form.get('address')
    sex = request.form.get('sex')
    dob_str = request.form.get('date_of_birth')

    if not email or not password or not confirm_password or not address or not sex or not dob_str or not name:
        flash('All registration fields are required.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        flash('Email already registered', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    try:
        date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Date of birth must be in YYYY-MM-DD format.', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    password_hash = generate_password_hash(password)

    new_user = Subscriber.create_new_subscriber(
        email=email,
        name=name,
        address=address,
        pswd_hash=password_hash,
        sex=sex,
        date_of_birth=date_of_birth,
        height = None,
        weight = None
    )

    session['user_id'] = new_user.subscriber_id
    flash('Registration successful, you are now logged in', 'success')
    return redirect(url_for('home'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))