import pytest, datetime
from flaskr import create_app, db

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

def test_db_tables(app):
    with app.app_context():
        # Check if tables are created
        from sqlalchemy import inspect
        from flaskr import db
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        assert 'subscriber' in tables
        assert 'food_diary' in tables
        assert 'meal' in tables
        assert 'meal_item' in tables
        assert 'food' in tables
        assert 'saved_meal' in tables
        assert 'professional' in tables
        assert 'comment' in tables
        assert 'recipe' in tables
        assert 'recipe_item' in tables
        assert 'favourite_recipe' in tables
        assert 'recipe_rating' in tables
        assert 'manages' in tables

def test_create_subscriber(app):
    # Test creating a new subscriber manually & verify it was added to the database
    with app.app_context():
        from flaskr import db
        from flaskr.models import Subscriber

        new_subscriber = Subscriber(
            email = 'john.doe@example.com',
            name='John Doe',
            address = '123 Main St',
            pswd_hash='hashed_password',
            sex = 'Male',
            date_of_birth= datetime.date(1990, 1, 1),
            height = 180.0,
            weight = 75.0
        )
        db.session.add(new_subscriber)
        db.session.commit()

        result = Subscriber.query.filter_by(email='john.doe@example.com').first()
        assert result is not None
        assert result.name == 'John Doe'

def test_meal_diary_relationship(app):
    # Test creating a subscriber with a food diary and verify the relationship
    with app.app_context():
        from flaskr import db
        from flaskr.models import Meal, FoodDiary

        diary = FoodDiary()
        db.session.add(diary)
        db.session.commit()

        meal = Meal(diary_id=diary.diary_id, meal_time=datetime.datetime.now())
        db.session.add(meal)
        db.session.commit()

        assert len(diary.meals) == 1

def test_duplicate_email_fails(app):
    # Ensure accounts with the same email cannot be created
    with app.app_context():
        from flaskr.models import Subscriber
        from flaskr import db
        from sqlalchemy.exc import IntegrityError

        sub1 = Subscriber(
            email="same@test.com",
            name='Joe Doe',
            address = '123 Side St',
            pswd_hash='hashed_password',
            sex = 'Male',
            date_of_birth= datetime.date(1991, 1, 1),
            height = 170.0,
            weight = 80.0)
        sub2 = Subscriber(
            email="same@test.com",
            name='John Doe',
            address = '123 Main St',
            pswd_hash='hashed_password',
            sex = 'Male',
            date_of_birth= datetime.date(1990, 1, 1),
            height = 180.0,
            weight = 75.0)
        db.session.add_all([sub1, sub2])
        
        with pytest.raises(IntegrityError):
            db.session.commit()