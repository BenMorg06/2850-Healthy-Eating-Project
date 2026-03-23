import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ALLOWED_EMAIL = 'test@mail.com'
ALLOWED_PASSWORD = '12345'

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)  # use init_app on the module-level db, not a new instance

    with app.app_context():
        from flaskr import models
        db.create_all()

    @app.route('/', methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            # Always start at login page when opening the app.
            session.pop('user_email', None)
            return render_template('login.html')

        if request.method == "POST":
            email = (request.form.get('email') or '').strip().lower()
            password = (request.form.get('password') or '').strip()

            if email == ALLOWED_EMAIL and password == ALLOWED_PASSWORD:
                session['user_email'] = email
                return redirect(url_for('dashboard'))

            return render_template(
                'login.html',
                login_error='Invalid email or password. Please try again.'
            )

    @app.route('/register', methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = (request.form.get('email') or '').strip().lower()
            password = (request.form.get('password') or '').strip()
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_email'):
            return redirect(url_for('login'))
        return render_template('dashboard.html')
    
    @app.route('/diary')
    def diary():
        if not session.get('user_email'):
            return redirect(url_for('login'))
        return render_template('diary.html')

    return app