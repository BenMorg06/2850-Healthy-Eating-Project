from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Professional, Manages, Meal, Comment
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

@pytest.fixture
def subscriber_meal(app, subscriber):
    with app.app_context():
        diary_id = db.session.get(Subscriber, subscriber).diary_id
        meal = Meal.create_new_meal(diary_id, meal_time=datetime.now())
        return meal.meal_id

class TestProfessionalFeatures:
    """Tests professional-specific features like client management."""
    
    def test_professional_can_invite_existing_client(self, logged_in_professional, app, subscriber, professional):
        response = logged_in_professional.post('/invite_client', data={'client_email': 'test@example.com'}, follow_redirects=True)
 
        assert response.status_code == 200
        assert b'This subscriber is now linked to your profile' in response.data
 
        with app.app_context():
            manages = Manages.get_by_professional(professional_id=professional)
        assert manages is not None
        assert subscriber in [m.subscriber_id for m in manages]

    def test_professional_invite_non_existing_client_flashes_error(self, client, professional):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True
        
        response = client.post('/invite_client', data={'client_email': 'nonexistent@example.com'}, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'No subscriber found with email nonexistent@example.com' in response.data

    def test_professional_can_view_client_diary(self, client, app, professional, subscriber):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True
        
        Manages.create_management_relationship(professional_id=professional, subscriber_id=subscriber)

        response = client.get(f'/diary?client_id={subscriber}')
        assert response.status_code == 200

    def test_professional_cannot_view_non_client_diary(self, client, app, professional, subscriber):        
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True
        
        response = client.get(f'/diary?client_id={subscriber}')
        assert response.status_code == 403

    def test_non_professional_cannot_view_client_diary(self, logged_in_client):
        response = logged_in_client.get('/diary?client_id=1')
        assert response.status_code == 403

    def test_professional_can_view_client_meal(self, client, app, professional, subscriber, subscriber_meal):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True

        Manages.create_management_relationship(professional_id=professional, subscriber_id=subscriber)

        response = client.get(f'/meal/{subscriber_meal}/view')
        assert response.status_code == 200

    def test_professional_cannot_view_non_client_meal(self, client, app, professional, subscriber, subscriber_meal):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True

        response = client.get(f'/meal/{subscriber_meal}/view')
        assert response.status_code == 403

    def test_professional_can_comment_on_client_meal(self, client, app, professional, subscriber, subscriber_meal):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True

        Manages.create_management_relationship(professional_id=professional, subscriber_id=subscriber)

        response = client.post(
            f'/meal/{subscriber_meal}/comment',
            data={'title': 'Good balance', 'body': 'Try to keep protein high in the afternoon.'},
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Comment added successfully.' in response.data

        with app.app_context():
            comment = Comment.query.filter_by(meal_id=subscriber_meal).first()
            assert comment is not None
            assert comment.title == 'Good balance'
            assert comment.body == 'Try to keep protein high in the afternoon.'

    def test_subscriber_can_see_professional_comment(self, logged_in_client, app, professional, subscriber, subscriber_meal):
        with app.app_context():
            Manages.create_management_relationship(professional_id=professional, subscriber_id=subscriber)
            Comment.create_new_comment(
                meal_id=subscriber_meal,
                professional_id=professional,
                title='Hydrate',
                body='Drink a glass of water before your next meal.'
            )

        response = logged_in_client.get(f'/meal/{subscriber_meal}/view')
        assert response.status_code == 200
        assert b'Drink a glass of water before your next meal.' in response.data

    def test_professional_cannot_comment_on_non_client_meal(self, client, app, professional, subscriber, subscriber_meal):
        with client.session_transaction() as sess:
            sess['user_id'] = professional
            sess['is_professional'] = True

        response = client.post(
            f'/meal/{subscriber_meal}/comment',
            data={'title': 'Unauthorized', 'body': 'You should not be able to comment.'},
            follow_redirects=True
        )

        assert response.status_code == 403
