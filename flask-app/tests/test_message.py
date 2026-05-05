import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import Message, Professional, Subscriber, Manages
from datetime import date, datetime
from werkzeug.security import generate_password_hash

### Fixtures

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def subscriber(app):
    with app.app_context():
        password_hash = generate_password_hash('testpass123')
        s = Subscriber.create_new_subscriber(
            email='test@example.com',
            name='Test User',
            address='123 St',
            pswd_hash=password_hash,
            sex='Male',
            date_of_birth=date(2000, 1, 1),
            height=175.0,
            weight=70.0
        )
        return s.subscriber_id

@pytest.fixture
def logged_in_subscriber(client, subscriber, app):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
    
    with client.session_transaction() as session:
        session['user_id'] = subscriber   
        session['is_professional'] = False
        session['_fresh'] = True
    return client

@pytest.fixture
def professional(app):
    with app.app_context():
        password_hash = generate_password_hash('propass123')
        p = Professional.create_new_professional(
            email='pro@example.com',
            name='Test Professional',
            address='456 Pro St',
            pswd_hash=password_hash,
            profession=None
        )
        return p.professional_id
    
@pytest.fixture
def logged_in_professional(client, professional, app):
    with app.app_context():
        p = db.session.get(Professional, professional)

    with client.session_transaction() as sess:
        sess['user_id'] = professional
        sess['is_professional'] = True
        sess['_fresh'] = True
    return client

### Tests