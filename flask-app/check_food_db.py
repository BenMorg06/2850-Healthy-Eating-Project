from flaskr import create_app, db
from flaskr.models import Food
import pandas as pd

app = create_app()

with app.app_context():
    food = Food.query.filter_by(food_id='18-127').first()
    print(food.food_name, food.kcal, food.carbs, food.protein, food.fats)