from datetime import datetime, date
from flaskr import create_app, db
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

class TestSubscriber:
    good_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # empty subscriber
    empty_subscriber = ()
    # empty email
    empty_email_subscriber = ('',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0  )
    # invalid email: missing @, domain, etc
    invalid_email_subscriber = ('invalid email',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0  )
    # empty name
    empty_name_subscriber = (
        'john.doe@example.com',
        '',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # invalid name
    invalid_name_subscriber = (
        'john.doe@example.com',
        '1234534 34@$*29',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # too long name
    # empty address
    empty_address_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # invalid address
    invalid_address_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '$^%* Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # too long address
    # empty password
    empty_password_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        '',
        'Male',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # invalid password
    # empty sex
    empty_sex_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        '',
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # invalid sex
    invalid_sex_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        12,
        date(1990, 1, 1),
        180.0,
        75.0    
    )
    # empty date of birth
    empty_date_of_birth_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        '',
        180.0,
        75.0    
    )
    # invalid date of birth
    invalid_date_of_birth_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        'dateofbirth',
        180.0,
        75.0    
    )
    # non-date date of birth
    non_date_date_of_birth_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        12345,
        180.0,
        75.0    
    )
    # empty height
    empty_height_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        '',
        75.0    
    )
    # invalid height
    invalid_height_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        'invalid_height',
        75.0    
    )
    # empty weight
    empty_weight_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        ''    
    )
    # invalid weight
    invalid_weight_subscriber = (
        'john.doe@example.com',
        'John Doe',
        '123 Main St',
        'hashed_password',
        'Male',
        date(1990, 1, 1),
        180.0,
        'invalid_weight'
    )

    def test_create_good_subscriber(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            Subscriber.create_new_subscriber(*self.good_subscriber)
            result = Subscriber.query.filter_by(email=self.good_subscriber[0]).first()
            assert result is not None
            assert result.name == self.good_subscriber[1]

    @pytest.mark.parametrize("subscriber",
    [
        empty_subscriber,
        empty_email_subscriber,
        invalid_email_subscriber,
        empty_name_subscriber,
        invalid_name_subscriber,
        empty_address_subscriber,
        invalid_address_subscriber,
        empty_password_subscriber,
        empty_sex_subscriber,
        invalid_sex_subscriber,
        empty_date_of_birth_subscriber,
        invalid_date_of_birth_subscriber,
        non_date_date_of_birth_subscriber,
        empty_height_subscriber,
        invalid_height_subscriber,
        empty_weight_subscriber,
        invalid_weight_subscriber
    ]
    )
    def test_create_bad_subscriber(self, app, subscriber):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            with pytest.raises(Exception):
                Subscriber.create_new_subscriber(subscriber)

    def test_get_subscriber_by_email(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            Subscriber.create_new_subscriber(*self.good_subscriber)
            result = Subscriber.query.filter_by(email=self.good_subscriber[0]).first()
            assert result is not None
            assert result.name == self.good_subscriber[1]

    def test_get_subscriber_by_email_not_found(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            Subscriber.create_new_subscriber(*self.good_subscriber)
            result = Subscriber.query.filter_by(email='newemail@test.com').first()
            assert result is None
    
    def test_delete_subscriber(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            Subscriber.create_new_subscriber(*self.good_subscriber)
            subscriber = Subscriber.query.filter_by(email=self.good_subscriber[0]).first()
            Subscriber.delete_subscriber(subscriber)
            result = Subscriber.query.filter_by(email=self.good_subscriber[0]).first()
            assert result is None

    def test_duplicate_email_fails(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber
            from sqlalchemy.exc import IntegrityError
            Subscriber.create_new_subscriber(*self.good_subscriber)
            with pytest.raises(IntegrityError):
                Subscriber.create_new_subscriber(*self.good_subscriber)

    def test_diary_created_on_registration(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Subscriber, FoodDiary
            Subscriber.create_new_subscriber(*self.good_subscriber)
            diary_id = Subscriber.query.filter_by(email=self.good_subscriber[0]).first().diary_id
            diary = FoodDiary.query.filter_by(diary_id=diary_id).first()
            assert diary is not None

# TODO: Add tests for professional
# TODO: Add tests for manages relationship between professional and subscriber

class TestProfessional:
    good_professional = (
        'professional@test.com',
        'John Doe',
        '123 Main St',
        '123-456-7890',
        'nutritionist'
    )
    empty_email_professional = (
        '',
        'John Doe',
        '123 Main St',
        '123-456-7890',
        'nutritionist'
    )
    invalid_email_professional = (
        'invalid email',
        'John Doe',
        '123 Main St',
        '123-456-7890',
        'nutritionist'
    )
    empty_name_professional = (
        'professional@test.com',
        '',
        '123 Main St',
        '123-456-7890',
        'nutritionist'
    )
    invalid_name_professional = (
        'professional@test.com',
        12313,
        '123 Main St',
        '123-456-7890',
        'nutritionist'
    )
    empty_address_professional = (
        'professional@test.com',
        'John Doe',
        '',
        '123-456-7890',
        'nutritionist'
    )
    invalid_address_professional = (
        'professional@test.com',
        'John Doe',
        True,
        '123-456-7890',
        'nutritionist'
    )
    empty_password_professional = (
        'professional@test.com',
        'John Doe',
        '123 Main St',
        '',
        'nutritionist'
    )
    empty_profession_professional = (
        'professional@test.com',
        'John Doe',
        '123 Main St',
        '123-456-7890',
        ''
    )
    invalid_profession_professional = (
        'professional@test.com',
        'John Doe',
        '123 Main St',
        '123-456-7890',
        12345
    )

    def test_create_professional(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Professional
            new_professional = Professional.create_new_professional(*self.good_professional)
            assert new_professional is not None
            result = Professional.query.filter_by(email=self.good_professional[0]).first()
            assert result is not None
            assert result.name == self.good_professional[1]

    @pytest.mark.parametrize("professional",
        [
            empty_email_professional,
            invalid_email_professional,
            empty_name_professional,
            invalid_name_professional,
            empty_address_professional,
            invalid_address_professional,
            empty_password_professional,
            empty_profession_professional,
            invalid_profession_professional
        ]
    )
    def test_create_bad_professional(self, app, professional):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Professional
            with pytest.raises(Exception):
                Professional.create_new_professional(professional)

    def test_get_professional_by_email(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Professional
            Professional.create_new_professional(*self.good_professional)
            result = Professional.query.filter_by(email=self.good_professional[0]).first()
            assert result is not None
            assert result.name == self.good_professional[1]

    def test_get_professional_by_email_not_found(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Professional
            Professional.create_new_professional(*self.good_professional)
            result = Professional.query.filter_by(email='test@email.com').first()
            assert result is None
    
    def test_delete_professional(self, app):
        with app.app_context():
            from flaskr import db
            from flaskr.models import Professional
            Professional.create_new_professional(*self.good_professional)
            professional = Professional.query.filter_by(email=self.good_professional[0]).first()
            Professional.delete_professional(professional)
            result = Professional.query.filter_by(email=self.good_professional[0]).first()
            assert result is None
    

# TODO: Add tests for meal and food diary, including relationships

