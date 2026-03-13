import pytest
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
