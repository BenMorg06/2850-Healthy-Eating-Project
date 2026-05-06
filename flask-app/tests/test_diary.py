from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Meal, MealItem, Food, SavedMeal
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
    s = Subscriber.create_new_subscriber(
        email='test@test.com',
        name='Test User',
        address='123 St',
        pswd_hash='hash',
        sex='Male',
        date_of_birth=date(2000, 1, 1),
        height=175.0,
        weight=70.0
    )
    return s.subscriber_id


@pytest.fixture
def logged_in_client(client, subscriber):
    with client.session_transaction() as session:
        session['user_id'] = subscriber
        session['_fresh'] = True

    return client


def test_diary_page_loads(logged_in_client):
    response = logged_in_client.get('/diary')
    assert response.status_code == 200


def test_create_meal(app, logged_in_client, subscriber):
    response = logged_in_client.get('/create_meal')
    # should redirect to edit page
    assert response.status_code == 302

    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = db.session.get(Meal, s.diary_id)
        assert meal is not None
        assert meal.diary_id == s.diary_id


def test_cancel_meal_deletes_it(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = logged_in_client.post(f'/meal/{meal_id}/cancel')
    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Meal, meal_id) is None


def test_favourite_meal(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = logged_in_client.post(
        f'/meal/{meal_id}/favourite',
        follow_redirects=True
        )
    assert response.status_code == 200
    assert b'Meal added to favourites' in response.data

    with app.app_context():
        saved = SavedMeal.query.filter_by(
            subscriber_id=subscriber,
            meal_id=meal_id
            ).first()
        assert saved is not None
        assert saved.meal_name is not None


def test_view_favourites_page_empty(logged_in_client):
    response = logged_in_client.get('/favourites')
    assert response.status_code == 200
    assert b'No favourite meals yet' in response.data


def test_view_favourites_page_with_meals(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        SavedMeal.create_new_saved_meal(subscriber, meal.meal_id, 'Test Meal')

    response = logged_in_client.get('/favourites')
    assert response.status_code == 200
    assert b'Favourite Meals' in response.data
    assert b'Test Meal' in response.data


def test_quick_add_favourite_meal(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        food = Food(
            food_id='F999',
            food_name='Chicken',
            kcal=165,
            kj=690,
            carbs=0,
            protein=31,
            fats=3.6,
            sugar=0,
            fibre=0
        )
        db.session.add(food)
        db.session.commit()
        MealItem.create_new_meal_item(meal.meal_id, 'F999', 100)
        SavedMeal.create_new_saved_meal(
            subscriber,
            meal.meal_id,
            'Chicken 100g'
            )
        initial_meal_count = Meal.query.filter_by(diary_id=s.diary_id).count()
        meal_id = meal.meal_id

    response = logged_in_client.post(
        f'/favourites/quick_add/{meal_id}',
        follow_redirects=True
        )
    assert response.status_code == 200
    assert b'Favourite meal added to your diary' in response.data

    with app.app_context():
        new_meal_count = Meal.query.filter_by(diary_id=s.diary_id).count()
        assert new_meal_count == initial_meal_count + 1


def test_finish_meal_flashes_message(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    with logged_in_client.session_transaction() as session:
        session['_flashes'] = []  # clear flashes

    response = logged_in_client.post(f'/meal/{meal_id}/finish')
    assert response.status_code == 302


def test_meal_view_loads(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = logged_in_client.get(f'/meal/{meal_id}/view')
    assert response.status_code == 200


def test_search_food_returns_results(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id
        food = Food(
            food_id='F001',
            food_name='Test Food',
            kcal=100,
            kj=100,
            carbs=20,
            protein=10,
            fats=5,
            sugar=0,
            fibre=0
        )
        db.session.add(food)
        db.session.commit()
        food_id = food.food_id

    response = logged_in_client.get(f'/meal/{meal_id}/search?q=Test')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['food_id'] == food_id


def test_add_meal_item(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id
        food = Food(
            food_id='F002',
            food_name='Another Food',
            kcal=150,
            kj=150,
            carbs=30,
            protein=15,
            fats=10,
            sugar=0,
            fibre=0
        )
        db.session.add(food)
        db.session.commit()
        food_id = food.food_id

    response = logged_in_client.post(
        f'/meal/{meal_id}/add_item',
        data={'food_id': food_id, 'weight': 100}
        )
    assert response.status_code == 302

    with app.app_context():
        items = MealItem.get_by_meal(meal_id)
        assert len(items) == 1
        assert items[0].food_id == food_id


def test_remove_meal_item(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id
        food = Food(
            food_id='F003',
            food_name='Food To Remove',
            kcal=200,
            kj=200,
            carbs=40,
            protein=20,
            fats=15,
            sugar=0,
            fibre=0
            )
        db.session.add(food)
        db.session.commit()
        food_id = food.food_id
        item = MealItem.create_new_meal_item(meal_id, food_id, 100)
        item_id = item.meal_item_id

    response = logged_in_client.post(f'/meal/{meal_id}/remove_item/{item_id}')
    assert response.status_code == 302

    with app.app_context():
        items = MealItem.get_by_meal(meal_id)
        assert len(items) == 0  # item was removed


def test_search_food_no_results(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = logged_in_client.get(
        f'/meal/{meal_id}/search?q=NonExistentFood'
        )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0


def test_cancel_nonexistent_meal(app, logged_in_client):
    response = logged_in_client.post('/meal/999/cancel')
    assert response.status_code == 404


def test_edit_meal_loads(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    response = logged_in_client.get(f'/meal/{meal_id}/edit')
    assert response.status_code == 200


def test_delete_meal(app, logged_in_client, subscriber):
    with app.app_context():
        s = db.session.get(Subscriber, subscriber)
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        meal_id = meal.meal_id

    with logged_in_client.session_transaction() as session:
        session['_flashes'] = []  # clear flashes

    response = logged_in_client.post(f'/meal/{meal_id}/delete')
    assert response.status_code == 302

    with app.app_context():
        assert db.session.get(Meal, meal_id) is None  # meal was deleted
