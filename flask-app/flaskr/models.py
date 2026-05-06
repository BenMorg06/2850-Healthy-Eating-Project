from flaskr.extensions import db
from datetime import datetime


class FoodDiary(db.Model):
    # Define FoodDiary columns from db diagram
    diary_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Define FoodDiary relationships
    meals = db.relationship('Meal', backref='food_diary')

    # CRUD methods for FoodDiary
    @classmethod
    def create_new_diary(cls, Subscriber):
        new_diary = cls()
        db.session.add(new_diary)
        db.session.commit()
        Subscriber.diary_id = new_diary.diary_id
        db.session.commit()
        return new_diary


class Subscriber(db.Model):
    # Define Subscriber columns from db diagram
    subscriber_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    activity_level = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    diary_id = db.Column(
        db.Integer,
        db.ForeignKey('food_diary.diary_id'),
        nullable=True
        )

    # Define Subscriber relationships
    food_diary = db.relationship('FoodDiary', backref='subscriber')
    saved_meals = db.relationship('SavedMeal', backref='subscriber')
    favourite_recipes = db.relationship(
        'FavouriteRecipe',
        backref='subscriber'
        )
    recipe_ratings = db.relationship('RecipeRating', backref='subscriber')
    managed_by = db.relationship('Manages', backref='subscriber')

    # Subscriber CRUD methods
    def get_id(self):
        return str(self.subscriber_id)

    @classmethod
    def create_new_subscriber(
        cls,
        email,
        name,
        address,
        pswd_hash,
        sex,
        date_of_birth,
        height=None,
        weight=None
    ):
        new_subscriber = cls(
            email=email,
            name=name,
            address=address,
            pswd_hash=pswd_hash,
            sex=sex,
            date_of_birth=date_of_birth,
            height=height,
            weight=weight
        )
        db.session.add(new_subscriber)
        db.session.commit()
        # Create a food diary for the new subscriber
        FoodDiary.create_new_diary(new_subscriber)
        return new_subscriber

    def delete_subscriber(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


class Meal(db.Model):
    # Define Meal columns from db diagram
    meal_id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(
        db.Integer,
        db.ForeignKey('food_diary.diary_id'),
        nullable=False
        )
    meal_time = db.Column(db.DateTime, nullable=False)

    # Define Meal relationships
    items = db.relationship(
        'MealItem',
        backref='meals',
        cascade='all, delete-orphan'
        )
    comments = db.relationship('Comment', backref='meal')
    saved_by = db.relationship(
        'SavedMeal',
        backref='meal',
        cascade='all, delete-orphan'
        )

    @classmethod
    def create_new_meal(cls, diary_id, meal_time):
        new_meal = cls(diary_id=diary_id, meal_time=meal_time)
        db.session.add(new_meal)
        db.session.commit()
        return new_meal

    @classmethod
    def get_by_id(cls, meal_id):
        return cls.query.filter_by(meal_id=meal_id).all()

    @classmethod
    def get_by_diary_id(cls, diary_id):
        # Used to list all meals within a subscribers diary
        meals = cls.query.filter_by(diary_id=diary_id).all()
        diary = FoodDiary.query.filter_by(diary_id=diary_id).first()
        if not diary:
            raise ValueError("FoodDiary does not exist.")
        return meals

    def update_meal_time(self, new_time):
        self.meal_time = new_time
        db.session.commit()

    def delete_meal(self):
        db.session.delete(self)
        db.session.commit()


class MealItem(db.Model):
    # Define MealItem columns from db diagram
    meal_item_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(
        db.Integer,
        db.ForeignKey('meal.meal_id'),
        nullable=False
        )
    food_id = db.Column(
        db.String(120),
        db.ForeignKey('food.food_id'),
        nullable=False
        )
    weight = db.Column(db.Integer, nullable=False)

    @classmethod
    def create_new_meal_item(cls, meal_id, food_id, weight):
        new_meal_item = cls(meal_id=meal_id, food_id=food_id, weight=weight)
        db.session.add(new_meal_item)
        db.session.commit()
        return new_meal_item

    @classmethod
    def get_by_meal(cls, meal_id):
        # Used to detail all food items within a single meal
        return cls.query.filter_by(meal_id=meal_id).all()

    def update_weight(self, new_weight):
        self.weight = new_weight
        db.session.commit()

    def delete_meal_item(self):
        db.session.delete(self)
        db.session.commit()


class Food(db.Model):
    # Define Food columns from db diagram
    # Import macros from MCance and Widdowson's CoFID
    food_id = db.Column(db.String(120), primary_key=True)
    food_name = db.Column(db.String(120), nullable=False)
    kcal = db.Column(db.Float, nullable=False)
    kj = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    sugar = db.Column(db.Float, nullable=False)
    fibre = db.Column(db.Float, nullable=False)

    # Define Food relationships
    meal_items = db.relationship('MealItem', backref='food')
    recipe_items = db.relationship('RecipeItem', backref='food')


# SavedMeal
class SavedMeal(db.Model):
    # Define SavedMeal columns from db diagram
    saved_meal_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=False
        )
    meal_name = db.Column(db.String(120), nullable=False)
    meal_id = db.Column(
        db.Integer,
        db.ForeignKey('meal.meal_id'),
        nullable=False
        )
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def create_new_saved_meal(cls, subscriber_id, meal_id, meal_name):
        existing = cls.query.filter_by(
            subscriber_id=subscriber_id,
            meal_id=meal_id
            ).first()
        if existing:
            return existing
        new_saved = cls(
            subscriber_id=subscriber_id,
            meal_id=meal_id,
            meal_name=meal_name
            )
        db.session.add(new_saved)
        db.session.commit()
        return new_saved

    @classmethod
    def get_by_subscriber(cls, subscriber_id):
        return cls.query.join(Meal)\
                .filter(cls.subscriber_id == subscriber_id)\
                .order_by(cls.saved_at.desc())\
                .all()

    @classmethod
    def delete_saved_meal(cls, subscriber_id, meal_id):
        saved = cls.query.filter_by(
            subscriber_id=subscriber_id,
            meal_id=meal_id
            ).first()
        if saved:
            db.session.delete(saved)
            db.session.commit()
            return True
        return False


#  Professional
class Professional(db.Model):
    # Define Professional columns from db diagram
    professional_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    profession = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # Define Professional relationships
    comments = db.relationship('Comment', backref='professional')
    manages = db.relationship('Manages', backref='professional')

    # CRUD methods for Professional
    @classmethod
    def create_new_professional(
        cls,
        email,
        name,
        address,
        pswd_hash,
        profession=None
    ):
        new_professional = cls(
            email=email,
            name=name,
            address=address,
            pswd_hash=pswd_hash,
            profession=profession
        )
        db.session.add(new_professional)
        db.session.commit()
        return new_professional

    def delete_professional(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def verify_password(self, password):
        # Implement password verification logic
        pass


# Manages
class Manages(db.Model):
    # Define Manages columns from db diagram
    manages_id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(
        db.Integer,
        db.ForeignKey('professional.professional_id'),
        nullable=False
        )
    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=False
        )
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)

    # CRUD for managing relationships between professionals and subscribers
    @classmethod
    def create_management_relationship(cls, professional_id, subscriber_id):
        new_relationship = cls(
            professional_id=professional_id,
            subscriber_id=subscriber_id
            )
        db.session.add(new_relationship)
        db.session.commit()
        return new_relationship

    @classmethod
    def get_by_professional(cls, professional_id):
        # Used to list all subscribers managed by a professional
        return cls.query.filter_by(professional_id=professional_id).all()

    @classmethod
    def get_by_subscriber(cls, subscriber_id):
        # Used to find the professional(s) managing a subscriber
        return cls.query.filter_by(subscriber_id=subscriber_id).all()

    def end_management(self):
        self.end_date = datetime.now()
        db.session.commit()


# Comment
class Comment(db.Model):
    # Define Comment columns from db diagram
    comment_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(
        db.Integer,
        db.ForeignKey('meal.meal_id'),
        nullable=False
        )
    professional_id = db.Column(
        db.Integer,
        db.ForeignKey('professional.professional_id'),
        nullable=False
        )
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # CRUD for commenting on meals
    @classmethod
    def create_new_comment(cls, meal_id, professional_id, title, body):
        new_comment = cls(
            meal_id=meal_id,
            professional_id=professional_id,
            title=title,
            body=body
        )
        db.session.add(new_comment)
        db.session.commit()
        return new_comment

    @classmethod
    def get_by_meal(cls, meal_id):
        # Used to list all comments on a meal, e.g. for a meal summary page
        return cls.query.filter_by(meal_id=meal_id).all()

    def update_comment(self, new_title, new_body):
        self.title = new_title
        self.body = new_body
        db.session.commit()

    def delete_comment(self):
        db.session.delete(self)
        db.session.commit()


# Recipe
class Recipe(db.Model):
    # Define Recipe columns from db diagram
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    num_of_servings = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # Photo field can be added later

    # Define Recipe relationships
    items = db.relationship('RecipeItem', backref='recipe')
    ratings = db.relationship('RecipeRating', backref='recipe')
    favourited_by = db.relationship('FavouriteRecipe', backref='recipe')


# RecipeItem
class RecipeItem(db.Model):
    # Define RecipeItem columns from db diagram
    recipe_item_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id'),
        nullable=False
        )
    food_id = db.Column(
        db.String(120),
        db.ForeignKey('food.food_id'),
        nullable=False
        )
    weight = db.Column(db.Integer, nullable=False)


# FavouriteRecipe
class FavouriteRecipe(db.Model):
    # Define FavouriteRecipe columns from db diagram
    favourite_recipe_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=False
        )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id'),
        nullable=False
        )
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


# Recipe Rating
class RecipeRating(db.Model):
    # Define RecipeRating columns from db diagram
    recipe_rating_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=False
        )
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id'),
        nullable=False
        )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


# Nutrition Score
class NutritionScore(db.Model):
    # Define NutritionScore columns from db diagram
    nutrition_score_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=False
        )
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Float, nullable=False)
    calorie_score = db.Column(db.Float, nullable=False)
    macro_score = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
        )

    @classmethod
    def create_new_score(
        cls,
        subscriber_id,
        date,
        score,
        calorie_score,
        macro_score
    ):
        new_score = cls(
            subscriber_id=subscriber_id,
            date=date,
            score=score,
            calorie_score=calorie_score,
            macro_score=macro_score
        )
        db.session.add(new_score)
        db.session.commit()
        return new_score


# Message
class Message(db.Model):
    # Define Message columns
    message_id = db.Column(db.Integer, primary_key=True)
    sender_professional_id = db.Column(
        db.Integer,
        db.ForeignKey('professional.professional_id'),
        nullable=True)
    sender_subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=True
    )
    recipient_professional_id = db.Column(
        db.Integer,
        db.ForeignKey('professional.professional_id'),
        nullable=True
    )
    recipient_subscriber_id = db.Column(
        db.Integer,
        db.ForeignKey('subscriber.subscriber_id'),
        nullable=True
    )
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    # Define Message relationships
    sender_professional = db.relationship(
        'Professional',
        foreign_keys=[sender_professional_id],
        backref='sent_messages'
        )
    sender_subscriber = db.relationship(
        'Subscriber',
        foreign_keys=[sender_subscriber_id],
        backref='sent_messages'
        )
    recipient_professional = db.relationship(
        'Professional',
        foreign_keys=[recipient_professional_id],
        backref='received_messages'
        )
    recipient_subscriber = db.relationship(
        'Subscriber',
        foreign_keys=[recipient_subscriber_id],
        backref='received_messages'
        )

    @classmethod
    def create_new_message(
        cls,
        sender_professional_id,
        sender_subscriber_id,
        recipient_professional_id,
        recipient_subscriber_id,
        subject,
        body
            ):
        new_message = cls(
            sender_professional_id=sender_professional_id,
            sender_subscriber_id=sender_subscriber_id,
            recipient_professional_id=recipient_professional_id,
            recipient_subscriber_id=recipient_subscriber_id,
            subject=subject,
            body=body
        )
        db.session.add(new_message)
        db.session.commit()
        return new_message

    @classmethod
    def get_conversation(
        cls,
        user1_professional_id,
        user1_subscriber_id,
        user2_professional_id,
        user2_subscriber_id
            ):
        # Get messages between two users
        return cls.query.filter(
            (
                ((cls.sender_professional_id == user1_professional_id)
                 & (cls.sender_subscriber_id == user1_subscriber_id) &
                 (cls.recipient_professional_id == user2_professional_id)
                 & (cls.recipient_subscriber_id == user2_subscriber_id)) |
                ((cls.sender_professional_id == user2_professional_id) &
                 (cls.sender_subscriber_id == user2_subscriber_id) &
                 (cls.recipient_professional_id == user1_professional_id) &
                 (cls.recipient_subscriber_id == user1_subscriber_id))
            )
        ).order_by(cls.sent_at).all()

    @classmethod
    def get_user_messages(cls, professional_id, subscriber_id):
        # Get all messages for a user
        return cls.query.filter(
            ((cls.sender_professional_id == professional_id)
             & (cls.sender_subscriber_id == subscriber_id)) |
            ((cls.recipient_professional_id == professional_id)
             & (cls.recipient_subscriber_id == subscriber_id))
        ).order_by(cls.sent_at.desc()).all()

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()
