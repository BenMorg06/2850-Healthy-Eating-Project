from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Meal, MealItem, Food
from datetime import date, datetime
import pytest
from werkzeug.security import generate_password_hash


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
def logged_in_client(client, subscriber, app):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
    
    with client.session_transaction() as session:
        session['user_id'] = subscriber   
        session['_fresh'] = True
    
    return client

class TestAuthRoutes:
    """Tests route access and basic functionality."""
    
    def test_login_get_shows_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_get_with_register_tab(self, client):
        """GET /login?tab=register should show register tab active."""
        response = client.get('/login?tab=register')
        assert response.status_code == 200

    def test_already_logged_in_redirects_from_login(self, logged_in_client):
        response = logged_in_client.get('/login')
        assert response.status_code == 302
        assert response.location.endswith('/')

    def test_already_logged_in_redirects_from_auth(self, logged_in_client):
        response = logged_in_client.get('/auth')
        assert response.status_code == 302
        assert response.location.endswith('/')