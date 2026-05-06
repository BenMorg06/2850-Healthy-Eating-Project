import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import Food, Subscriber, Meal
from datetime import date, datetime
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
def meal_id(subscriber):
    s = db.session.get(Subscriber, subscriber)
    meal = Meal.create_new_meal(s.diary_id, datetime.now())
    return meal.meal_id


@pytest.fixture
def subscriber():
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
    with client.session_transaction() as session:
        session['user_id'] = subscriber
        session['_fresh'] = True

    return client


@pytest.fixture
def food_db(app):
    foods = [
        Food(
            food_id='F001',
            food_name='Salmon, smoked, cold-smoked',
            kcal=184,
            kj=770,
            protein=22.8,
            carbs=0.5,
            fats=10.1,
            sugar=0,
            fibre=0),
        Food(
            food_id='F002',
            food_name='Salmon, smoked, hot-smoked',
            kcal=173,
            kj=724,
            protein=23.5,
            carbs=0,
            fats=9.0,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F003',
            food_name='Salmon, pink, canned',
            kcal=153,
            kj=640,
            protein=23.5,
            carbs=0,
            fats=6.5,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F004',
            food_name='Cheese, processed, smoked',
            kcal=303,
            kj=1268,
            protein=20.5,
            carbs=0.2,
            fats=24.5,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F005',
            food_name='Mackerel, flesh only, smoked',
            kcal=301,
            kj=1260,
            protein=21.1,
            carbs=0,
            fats=24.1,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F006',
            food_name='Chicken, breast, grilled',
            kcal=148,
            kj=620,
            protein=32.0,
            carbs=0,
            fats=2.2,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F007',
            food_name='Chicken, breast, raw',
            kcal=105,
            kj=440,
            protein=22.0,
            carbs=0,
            fats=1.7,
            sugar=0,
            fibre=0
            ),
        Food(
            food_id='F008',
            food_name='Beef, mince, raw',
            kcal=225,
            kj=942,
            protein=17.5,
            carbs=0,
            fats=17.5,
            sugar=0,
            fibre=0
            )
    ]
    for f in foods:
        db.session.add(f)
    db.session.commit()


class TestSearchResults:
    def test_exact_match(self, logged_in_client, meal_id, food_db):
        response = logged_in_client.get(
            f'/meal/{meal_id}/search?q=Salmon, smoked, hot-smoked'
            )
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        assert data[0]['food_name'] == 'Salmon, smoked, hot-smoked'

    def test_partial_match_returns_results(
            self,
            logged_in_client,
            meal_id,
            food_d
            ):
        response = logged_in_client.get(f'/meal/{meal_id}/search?q=salm')
        data = response.get_json()
        assert any('Salmon' in r['food_name'] for r in data)

    def test_returns_correct_fields(self, logged_in_client, meal_id, food_db):
        response = logged_in_client.get(f'/meal/{meal_id}/search?q=chicken')
        data = response.get_json()

        assert len(data) > 0
        for result in data:
            assert 'food_id' in result
            assert 'food_name' in result
            assert 'kcal' in result
            assert 'protein' in result
            assert 'carbs' in result
            assert 'fats' in result

    def test_empty_query_returns_empty_list(self, logged_in_client, meal_id):
        response = logged_in_client.get(f'/meal/{meal_id}/search?q=')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_no_match_returns_empty_list(self, logged_in_client, meal_id):
        response = logged_in_client.get(
            f'/meal/{meal_id}/search?q=xyznonexistentfood'
            )
        assert response.status_code == 200
        assert response.get_json() == []

    # Fails as currently returns closet matches even if very poor
    def test_no_match_with_space(self, logged_in_client, meal_id):
        response = logged_in_client.get(
            f'/meal/{meal_id}/search?q=Nonexistent Food'
            )
        assert response.status_code == 200
        assert response.get_json() == []

    def test_case_insensitive_search(self, logged_in_client, meal_id):
        lower = logged_in_client.get(
            f'/meal/{meal_id}/search?q=chicken'
            ).get_json()
        upper = logged_in_client.get(
            f'/meal/{meal_id}/search?q=CHICKEN'
            ).get_json()
        mixed = logged_in_client.get(
            f'/meal/{meal_id}/search?q=ChIcKeN'
            ).get_json()

        assert [r['food_id'] for r in lower] == \
               [r['food_id'] for r in upper] == \
               [r['food_id'] for r in mixed]

    def test_whitespace_only_query_returns_empty_list(
            self,
            logged_in_client,
            meal_id
            ):
        response = logged_in_client.get(f'/meal/{meal_id}/search?q=   ')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_missing_query_param_returns_empty_list(
            self,
            logged_in_client,
            meal_id
            ):
        response = logged_in_client.get(f'/meal/{meal_id}/search')
        assert response.status_code == 200
        assert response.get_json() == []


class TestSearchRanking:
    def test_first_word_boost(self, logged_in_client, meal_id, food_db):
        response = logged_in_client.get(f'/meal/{meal_id}/search?q=Salmon')
        data = response.get_json()
        assert len(data) > 0
        assert data[0]['food_name'].startswith('Salmon')

    def test_all_words_boost(self, logged_in_client, meal_id, food_db):
        response = logged_in_client.get(
            f'/meal/{meal_id}/search?q=Smoked Salmon'
            )
        data = response.get_json()
        assert len(data) > 0
        assert data[0]['food_name'].startswith('Salmon')\
            and 'smoked' in data[0]['food_name']
