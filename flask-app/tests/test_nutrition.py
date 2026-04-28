from datetime import date, datetime
import pytest
from werkzeug.security import generate_password_hash
from flaskr.extensions import db
from flaskr import create_app
from flaskr.models import Subscriber, Meal, MealItem, Food
from flaskr.nutrition import calculate_bmr, calculate_caloric_need, calculate_daily_score, aggregate_meal_nutrition, load_subscriber_meals_for_date, update_nutrition_score
 
 

### Fixtures  

@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
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
            email='test@example.com',
            name='Test User',
            address='123 St',
            pswd_hash=generate_password_hash('testpass123'),
            sex='Male',
            date_of_birth=date(1990, 1, 1),
            height=175.0,
            weight=70.0,
        )
        s.activity_level = 'Moderately Active'
        db.session.commit()
        return s.subscriber_id
 
 
@pytest.fixture
def incomplete_subscriber(app):
    """Subscriber missing sex/height/weight — caloric need cannot be calculated."""
    with app.app_context():
        s = Subscriber.create_new_subscriber(
            email='incomplete@example.com',
            name='Incomplete User',
            address='456 St',
            pswd_hash=generate_password_hash('testpass123'),
            sex=None,
            date_of_birth=None,
            height=None,
            weight=None,
        )
        db.session.commit()
        return s.subscriber_id
 
 
@pytest.fixture
def logged_in_client(client, subscriber):
    with client.session_transaction() as sess:
        sess['user_id'] = subscriber
        sess['_fresh'] = True
    return client
 
### Helpers

def make_food(app, kcal=200, protein=10, carbs=30, fats=5, sugar=8, fibre=3):
    """Insert a Food row and return its id."""
    with app.app_context():
        food = Food(kcal=kcal, protein=protein, carbs=carbs, fats=fats, sugar=sugar, fibre=fibre)
        db.session.add(food)
        db.session.commit()
        return food.food_id
 
 
def make_meal_for_subscriber(app, subscriber_id, food_id, weight=100, meal_date=None):
    """Insert a Meal + MealItem for the given subscriber and return the meal id."""
    with app.app_context():
        s = db.session.get(Subscriber, subscriber_id)
        meal_time = datetime.combine(meal_date or date.today(), datetime.min.time())
        meal = Meal(diary_id=s.diary_id, meal_time=meal_time)
        db.session.add(meal)
        db.session.flush()
        item = MealItem(meal_id=meal.meal_id, food_id=food_id, weight=weight)
        db.session.add(item)
        db.session.commit()
        return meal.meal_id
    
class TestCalculateBmr:
    pass

class TestCalculateCaloricNeed:
    pass

class TestAggregateMealNutrition:
    pass

class TestCalculateDailyScore:
    pass

class TestDashboard:
    pass