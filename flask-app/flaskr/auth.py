from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import check_password_hash
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
            flash('Registration currently not enabled. Please use seeded test accounts.', 'info')
            return redirect(url_for('auth.login', tab='login'))

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
    # Minimal register support: implement your own validation and user creation.
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('username') or 'New User'

    if not email or not password:
        flash('Email and password are required', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    existing = Subscriber.query.filter_by(email=email).first()
    if existing:
        flash('Email already registered', 'error')
        return redirect(url_for('auth.auth_page', tab='register'))

    # TODO: hash password and create Subscriber object properly
    flash('Registration flow is not enabled yet. Please use seeded test accounts.', 'info')
    return redirect(url_for('auth.auth_page', tab='login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))