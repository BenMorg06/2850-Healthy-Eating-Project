from flaskr import db
from datetime import datetime

# TODO: Write tests for database
# TODO: Add methods to models for CRUD ops

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

class Subscriber(db.Model):
    # Define Subscriber columns from db diagram
    subscriber_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    diary_id = db.Column(db.Integer, db.ForeignKey('food_diary.diary_id'), nullable=True)

    # Define Subscriber relationships
    food_diary = db.relationship('FoodDiary', backref='subscriber')
    saved_meals = db.relationship('SavedMeal', backref='subscriber')
    favourite_recipes = db.relationship('FavouriteRecipe', backref='subscriber')
    recipe_ratings = db.relationship('RecipeRating', backref='subscriber')
    managed_by = db.relationship('Manages', backref='subscriber')

    # Subscriber CRUD methods

    @classmethod
    def create_new_subscriber(cls, email, name, address, pswd_hash, sex, date_of_birth, height, weight):
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
        FoodDiary.create_new_diary(new_subscriber)  # Create a food diary for the new subscriber

    def delete_subscriber(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def verify_password(self, password):
        # Implement password verification logic
        pass


class Meal(db.Model):
    # Define Meal columns from db diagram
    meal_id = db.Column(db.Integer, primary_key=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('food_diary.diary_id'), nullable=False)
    meal_time = db.Column(db.DateTime, nullable=False)

    # Define Meal relationships
    items = db.relationship('MealItem', backref='meals')
    comments = db.relationship('Comment', backref='meal')
    saved_by = db.relationship('SavedMeal', backref='meal')

class MealItem(db.Model):
    # Define MealItem columns from db diagram
    meal_item_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    food_id = db.Column(db.String(120), db.ForeignKey('food.food_id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

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
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    meal_name = db.Column(db.String(120), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

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

    # Define Professional relationships
    comments = db.relationship('Comment', backref='professional')
    manages = db.relationship('Manages', backref='professional')

    # CRUD methods for Professional
    def create_new_professional(self, email, name, address, pswd_hash, profession):
        new_professional = Professional(
            email=email,
            name=name,
            address=address,
            pswd_hash=pswd_hash,
            profession=profession
        )
        db.session.add(new_professional)
        db.session.commit()

    def delete_professional(self):
        db.session.delete(self)
        db.session.commit()

    def get_by_email(self, email):
        return Professional.query.filter_by(email=email).first()
    
    def verify_password(self, password):
        # Implement password verification logic
        pass

# Manages
class Manages(db.Model):
    # Define Manages columns from db diagram
    manages_id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=True)

# Comment
class Comment(db.Model):
    # Define Comment columns from db diagram
    comment_id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

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
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    food_id = db.Column(db.String(120), db.ForeignKey('food.food_id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

# FavouriteRecipe
class FavouriteRecipe(db.Model):
    # Define FavouriteRecipe columns from db diagram
    favourite_recipe_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    saved_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

# Recipe Rating
class RecipeRating(db.Model):
    # Define RecipeRating columns from db diagram
    recipe_rating_id = db.Column(db.Integer, primary_key=True)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.subscriber_id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    rated_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
