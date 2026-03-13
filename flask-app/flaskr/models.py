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

# SavedMeal
class SavedMeal(db.Model):
    # Define SavedMeal columns from db diagram
    saved_meal_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    meal_name = db.Column(db.String(120), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define SavedMeal relationships

#  Professional
class Professional(db.Model):
    # Define Professional columns from db diagram
    professional_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    profession = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define Professional relationships

# Manages
class Manages(db.Model):
    # Define Manages columns from db diagram
    manages_id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)

    # TODO: Define Manages relationships

# Comment
class Comment(db.Model):
    # Define Comment columns from db diagram
    comment_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define Comment relationships

# Recipe
class Recipe(db.Model):
    # Define Recipe columns from db diagram
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    num_of_servings = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # Photo field can be added later
    
    # TODO: Define Recipe relationships

# RecipeItem
class RecipeItem(db.Model):
    # Define RecipeItem columns from db diagram
    recipe_item_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    food_id = db.Column(db.String(120), db.ForeignKey('food.food_id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    # TODO: Define RecipeItem relationships

# FavouriteRecipe
class FavouriteRecipe(db.Model):
    # Define FavouriteRecipe columns from db diagram
    favourite_recipe_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define FavouriteRecipe relationships

# Recipe Rating
class RecipeRating(db.Model):
    # Define RecipeRating columns from db diagram
    recipe_rating_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # TODO: Define RecipeRating relationships