import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import Message, Professional, Subscriber, Manages
from datetime import date
from werkzeug.security import generate_password_hash

# Fixtures


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
    with client.session_transaction() as sess:
        sess['user_id'] = professional
        sess['is_professional'] = True
        sess['_fresh'] = True
    return client

# Tests


class TestMessageRoute:
    def test_messages_page_loads_for_subscriber(self, logged_in_subscriber):
        response = logged_in_subscriber.get('/messages')
        assert response.status_code == 200

    def test_messages_page_loads_for_professional(
            self,
            logged_in_professional
            ):
        response = logged_in_professional.get('/messages')
        assert response.status_code == 200

    def test_redirects_to_login_if_not_authenticated(self, client):
        response = client.get('/messages')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']


class TestConversation:
    def test_view_empty_coversation(self, logged_in_subscriber, professional):
        response = logged_in_subscriber.get(f'/messages/{professional}/0')
        assert response.status_code == 200

    def test_view_conversation_with_messages(
            self,
            logged_in_subscriber,
            professional,
            app,
            client
            ):
        with client.session_transaction() as sess:
            user_id = sess['user_id']

        with app.app_context():
            s = db.session.get(Subscriber, user_id)
            Manages.create_management_relationship(
                professional,
                s.subscriber_id
                )
            Message.create_new_message(
                sender_professional_id=professional,
                sender_subscriber_id=None,
                recipient_professional_id=None,
                recipient_subscriber_id=s.subscriber_id,
                subject="Test Message",
                body="Hello from the professional!"
            )

        response = logged_in_subscriber.get(f'/messages/{professional}/0')
        assert response.status_code == 200
        assert b"Hello from the professional!" in response.data


class TestSendMessage:
    def test_unauthenticated_send_returns_403(
            self,
            client,
            professional,
            subscriber
            ):
        response = client.post('/messages/send', data={
            'recipient_professional_id': professional,
            'recipient_subscriber_id': 0,
            'subject': 'Hello',
            'body': 'Hi there'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

    def test_subscriber_sends_to_managed_professional(
            self,
            app,
            logged_in_subscriber,
            professional,
            subscriber
            ):
        Manages.create_management_relationship(professional, subscriber)
        response = logged_in_subscriber.post('/messages/send', data={
            'recipient_professional_id': professional,
            'recipient_subscriber_id': 0,
            'sender_professional_id': 0,
            'sender_subscriber_id': subscriber,
            'subject': 'Test subject',
            'body': 'Test body'
        })
        assert response.status_code == 302
        msg = Message.query.first()
        assert msg is not None
        assert msg.subject == 'Test subject'
        assert msg.sender_subscriber_id == subscriber

    def test_professional_sends_to_managed_subscriber(
            self,
            app,
            logged_in_professional,
            professional,
            subscriber
            ):
        Manages.create_management_relationship(professional, subscriber)
        response = logged_in_professional.post('/messages/send', data={
            'recipient_professional_id': 0,
            'recipient_subscriber_id': subscriber,
            'subject': 'Dietary advice',
            'body': 'Eat more greens'
        })
        assert response.status_code == 302
        msg = Message.query.first()
        assert msg is not None
        assert msg.sender_professional_id == professional

    def test_subscriber_blocked_without_relationship(
            self,
            app,
            logged_in_subscriber,
            professional,
            subscriber
            ):
        response = logged_in_subscriber.post('/messages/send', data={
            'recipient_professional_id': professional,
            'recipient_subscriber_id': 0,
            'subject': 'Unauthorized',
            'body': 'Should be blocked'
        })
        assert response.status_code == 403
        assert Message.query.count() == 0

    def test_professional_blocked_without_relationship(
            self,
            app,
            logged_in_professional,
            professional,
            subscriber
            ):
        response = logged_in_professional.post('/messages/send', data={
            'recipient_professional_id': 0,
            'recipient_subscriber_id': subscriber,
            'subject': 'Unauthorized',
            'body': 'Should be blocked'
        })
        assert response.status_code == 403
        assert Message.query.count() == 0
