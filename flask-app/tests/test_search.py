import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import Food, Subscriber, Meal
from datetime import date, datetime

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
def meal_id(app):
    with app.app_context():
        s = Subscriber.create_new_subscriber(
            email='test@example.com', 
            name='Test User',
            address='123 St',
            pswd_hash='hash',
            sex='Male',
            date_of_birth=date(2000, 1, 1),
            height=175.0,
            weight=70.0
        )
        meal = Meal.create_new_meal(s.diary_id, datetime.now())
        return meal.meal_id
    
@pytest.fixture
def food_db(app):
    with app.app_context():
        foods = [
            Food(food_id='F001', food_name='Salmon, smoked, cold-smoked',
                 kcal=184, kj=770, protein=22.8, carbs=0.5, fats=10.1, sugar=0, fibre=0),
            Food(food_id='F002', food_name='Salmon, smoked, hot-smoked',
                 kcal=173, kj=724, protein=23.5, carbs=0,   fats=9.0,  sugar=0, fibre=0),
            Food(food_id='F003', food_name='Salmon, pink, canned',
                 kcal=153, kj=640, protein=23.5, carbs=0,   fats=6.5,  sugar=0, fibre=0),
            Food(food_id='F004', food_name='Cheese, processed, smoked',
                 kcal=303, kj=1268, protein=20.5, carbs=0.2, fats=24.5, sugar=0, fibre=0),
            Food(food_id='F005', food_name='Mackerel, flesh only, smoked',
                 kcal=301, kj=1260, protein=21.1, carbs=0,   fats=24.1, sugar=0, fibre=0),
            Food(food_id='F006', food_name='Chicken, breast, grilled',
                 kcal=148, kj=620, protein=32.0, carbs=0,   fats=2.2,  sugar=0, fibre=0),
            Food(food_id='F007', food_name='Chicken, breast, raw',
                 kcal=105, kj=440, protein=22.0, carbs=0,   fats=1.7,  sugar=0, fibre=0),
            Food(food_id='F008', food_name='Beef, mince, raw',
                 kcal=225, kj=942, protein=17.5, carbs=0,   fats=17.5, sugar=0, fibre=0),
        ]
        for f in foods:
            db.session.add(f)
        db.session.commit()
