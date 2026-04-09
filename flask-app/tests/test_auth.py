from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Meal, MealItem, Food, Professional
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
def logged_in_professional(client, professional):
    with client.session_transaction() as sess:
        sess['user_id'] = professional
        sess['is_professional'] = True
    return client

class TestAuthRoutes:
    """Tests route access and basic functionality."""
    
    def test_login_get_shows_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_login_get_with_register_tab(self, client):
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

class TestLogin:
    """Tests login functionality."""
    
    @pytest.mark.parametrize('user', [
        {'email': 'test@example.com',
         'password': 'testpass123',
         'form_type': 'login'},
        {'email': 'pro@example.com',
         'password': 'propass123',
         'form_type': 'login'}])
    def test_login_with_valid_credentials(self, client, user):
        response = client.post('/login', data={
            'email': user['email'],
            'password': user['password'],
            'form_type': user['form_type']
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_professional_login_sets_session_flags(self, client, professional):
        client.post('/login', data={
            'email': 'pro@example.com',
            'password': 'propass123',
            'form_type': 'login'
        }, follow_redirects=False)

        with client.session_transaction() as sess:
            assert sess['user_id'] == professional
            assert sess['is_professional'] == True

    def test_subscriber_login_does_not_set_professional_flag(self, client, subscriber):
        client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpass123',
            'form_type': 'login'
        }, follow_redirects=False)

        with client.session_transaction() as sess:
            assert sess.get('is_professional') is None

    def test_login_with_invalid_password(self, client):
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpass',
            'form_type': 'login'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

    def test_valid_login_sets_session_id(self, client, subscriber):
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpass123',
            'form_type': 'login'
        }, follow_redirects=False)

        with client.session_transaction() as session:
            assert 'user_id' in session
            assert session['user_id'] is not None
    
    def test_login_with_invalid_email(self, client):
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'testpass123',
            'form_type': 'login'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

    def test_login_with_missing_fields(self, client):
        response = client.post('/login', data={
            'email': '',
            'password': '',
            'form_type': 'login'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid email or password' in response.data

class TestRegistration:
    """Tests registration functionality."""
    
    def test_registration_with_valid_data(self, client):
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'address': '456 Ave',
            'password': 'newpass456',
            'confirm_password': 'newpass456',
            'sex': 'Female',
            'date_of_birth': '2000-01-01',
            'height': 165.0,
            'weight': 60.0
        }, follow_redirects=True)

        assert response.status_code == 200

    def test_registration_with_missing_fields(self, client):
        response = client.post('/register', data={
            'email': '',
            'name': '',
            'address': '',
            'password': '',
            'confirm_password': '',
            'sex': '',
            'date_of_birth': '',
            'height': '',
            'weight': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'error' in response.data

    def test_registration_with_password_mismatch(self, client):
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'address': '456 Ave',
            'password': 'newpass456',
            'confirm_password': 'wrongpass456',
            'sex': 'Female',
            'date_of_birth': '2000-01-01',
            'height': 165.0,
            'weight': 60.0
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Passwords do not match.' in response.data

    def test_registration_with_existing_email(self, client):
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'address': '123 St',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'sex': 'Male',
            'date_of_birth': '2000-01-01',
            'height': 175.0,
            'weight': 70.0
        }

        client.post('/register', data=data, follow_redirects=True)

        response = client.post('/register', data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b'Email already registered' in response.data
        
    def test_registration_with_invalid_dob_format(self, client):
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'address': '456 Ave',
            'password': 'newpass456',
            'confirm_password': 'newpass456',
            'sex': 'Female',
            'date_of_birth': 'invalid-date',
            'height': 165.0,
            'weight': 60.0
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Date of birth must be in YYYY-MM-DD format' in response.data

    def test_registration_with_invalid_email_format(self, client):
        response = client.post('/register', data={
            'email': 'invalid-email',
            'name': 'New User',
            'address': '456 Ave',
            'password': 'newpass456',
            'confirm_password': 'newpass456',
            'sex': 'Male',
            'date_of_birth': '2000-01-01',
            'height': 165.0,
            'weight': 60.0
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Invalid email format' in response.data

    def test_registration_with_professional_flag(self, client, app):
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'address': '456 Ave',
            'password': 'newpass456',
            'confirm_password': 'newpass456',
            'sex': 'Male',
            'date_of_birth': '2000-01-01',
            'is_professional': 'true'
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            pro = Professional.query.filter_by(email='newuser@example.com').first()
            assert pro is not None

    def test_register_creates_diary_for_user(self, client, app):
        response = client.post('/register', data={
            'email': 'diarynewuser@example.com',
            'name': 'Diary User',
            'address': '777 Diary St',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123',
            'sex': 'Other',
            'date_of_birth': '1994-02-28',
            'form_type': 'register'
        }, follow_redirects=False)
        
        with app.app_context():
            user = Subscriber.query.filter_by(email='diarynewuser@example.com').first()
            assert user is not None
            assert user.diary_id is not None

class TestLogout:
    """Tests logout functionality."""
    
    def test_logout_clears_session(self, logged_in_client):
        response = logged_in_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302

        with logged_in_client.session_transaction() as session:
            assert 'user_id' not in session
            assert '_fresh' not in session

    def test_logout_redirects_to_login(self, client, subscriber):
        with client.session_transaction() as sess:
            sess['user_id'] = subscriber
        
        response = client.get('/logout', follow_redirects=False)
        
        assert response.status_code == 302
        assert '/login' in response.location

    def test_logout_shows_flash_message(self, client, subscriber):
        with client.session_transaction() as sess:
            sess['user_id'] = subscriber
        
        response = client.get('/logout', follow_redirects=True)
        
        assert b'You have been logged out' in response.data

class TestAuthAccessControl:
    """Tests that protected routes require authentication."""
    
    def test_unauthenticated_access_to_diary_requires_login(self, client):
        response = client.get('/diary', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_unauthenticated_access_to_dashboard_requires_login(self, client):
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location
    
    def test_unauthenticated_access_to_meal_requires_login(self, client):
        response = client.get('/create_meal', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_authenticated_access_to_diary_successful(self, logged_in_client):
        response = logged_in_client.get('/diary', follow_redirects=False)
        assert response.status_code == 200

    def test_authenticated_access_to_dashboard_successful(self, logged_in_client):
        response = logged_in_client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 200

    def test_authenticated_access_to_meal_successful(self, logged_in_client):
        response = logged_in_client.get('/create_meal', follow_redirects=False)
        assert response.status_code == 302  # should redirect to edit page
    
    def test_unauthenticated_access_to_professional_dashboard_requires_login(self, client):
        response = client.get('/professional_dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.location

    def test_professional_can_access_professional_dashboard(self, client, app):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['is_professional'] = True
        response = client.get('/professional_dashboard', follow_redirects=False)
        assert response.status_code == 200

    def test_non_professional_cannot_access_invite_client(self, logged_in_client):
        response = logged_in_client.get('/invite_client', follow_redirects=False)
        assert response.status_code == 302

    def test_professional_dashboard_redirects_from_home(self, client):
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['is_professional'] = True
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'professional_dashboard' in response.location