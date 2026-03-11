from flaskr import db
from datetime import datetime

class Subscriber(db.Model):
    # Define Subscriber columns from db diagram
    subscriber_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    diary_id = db.Column(db.Integer, db.ForeignKey('food_diary.diary_id'), nullable=False)

    # TODO: Define Subscriber relationships

class FoodDiary(db.Model):
    # Define FoodDiary columns from db diagram
    diary_id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define FoodDiary relationships

class Meal(db.Model):
    # Define Meal columns from db diagram
    meal_id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('food_diary.diary_id'), nullable=False)
    meal_time = db.Column(db.DateTime, nullable=False)

    # TODO: Define Meal relationships

class MealItem(db.Model):
    # Define MealItem columns from db diagram
    meal_item_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    food_id = db.Column(db.String(120), db.ForeignKey('food.food_id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    # TODO: Define MealItem relationships

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

    # TODO: Define Food relationships

# TODO: SavedMeal

# TODO: Professional

# TODO: Manages

# TODO: Comment

# TODO: Recipe

# TODO: RecipeItem

# TODO: FavouriteRecipe
