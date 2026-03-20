from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Meal, MealItem, Food
from datetime import date, datetime
import pytest


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
        s = Subscriber.create_new_subscriber(
            email='test@test.com', 
            name='Test User',
            address='123 St',
            pswd_hash='hash',
            sex='M',
            date_of_birth=date(2000, 1, 1),
            height=175.0,
            weight=70.0
        )
        return s.subscriber_id

def test_diary_page_loads(client, subscriber):
    response = client.get('/diary')
    assert response.status_code == 200

def test_create_meal(app, client, subscriber):
    response = client.get('/create_meal')
    assert response.status_code == 302  # should redirect to edit page

    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = db.session.get(Meal, s.diary_id)
        assert meal is not None
        assert meal.diary_id == s.diary_id

def test_cancel_meal_deletes_it(app, client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = client.post(f'/meal/{meal_id}/cancel')
    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Meal, meal_id) is None  # meal was deleted

def test_finish_meal_flashes_message(app, client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    with client.session_transaction() as session:
        session['_flashes'] = []  # clear flashes

    response = client.post(f'/meal/{meal_id}/finish')
    assert response.status_code == 302

def test_meal_view_loads(app, client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = client.get(f'/meal/{meal_id}/view')
    assert response.status_code == 200