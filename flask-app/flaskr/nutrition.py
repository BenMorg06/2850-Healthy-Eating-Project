
from datetime import date

def calculate_daily_score(meals, nutrition_data, subscriber):
    '''
    Calorie Score: (Total Calories Consumed / Caloric Need) * 100, capped at 150% over
    Macro Score: Average of carbs (45-65%), protein (10-35%), fat (20-35%) scores
    Each macro: 100 if in range, scaled down if outside
    '''
    caloric_need = calculate_caloric_need(subscriber)
    if caloric_need is None or nutrition_data['calories'] == 0:
        return 0, 0, 0
    
    calorie_score = min(150, nutrition_data['calories'] / caloric_need * 100)
    
    # Macro targets as % of calories
    macro_ranges = {
        'carbs': (45, 65),
        'protein': (10, 35),
        'fat': (20, 35)
    }
    
    macro_scores = []
    for macro, (min_pct, max_pct) in macro_ranges.items():
        grams_to_cal = {'carbs': 4, 'protein': 4, 'fat': 9}[macro]
        actual_cal = nutrition_data[macro] * grams_to_cal
        actual_pct = (actual_cal / nutrition_data['calories']) * 100
        
        if min_pct <= actual_pct <= max_pct:
            score = 100
        elif actual_pct < min_pct:
            score = max(0, (actual_pct / min_pct) * 100)
        else:
            score = max(0, ((max_pct * 2 - actual_pct) / max_pct) * 100)
        macro_scores.append(score)
    
    macro_score = sum(macro_scores) / len(macro_scores)
    nutrition_score = 0.5 * calorie_score + 0.5 * macro_score  # Equal weight
    print(f"Calorie Score: {calorie_score:.2f}, Macro Score: {macro_score:.2f}, Nutrition Score: {nutrition_score:.2f}")
    return nutrition_score, calorie_score, macro_score

def calculate_bmr(subscriber):
    age = subscriber.date_of_birth and (date.today().year - subscriber.date_of_birth.year)
    if age is None or subscriber.height is None or subscriber.weight is None or subscriber.sex is None:
        return None
    if subscriber.sex == 'Male':
        bmr = 66.5 + (13.75 * subscriber.weight) + (5 * subscriber.height) - (6.75 * age)
        return bmr
    elif subscriber.sex == 'Female':
        bmr = 655.1 + (9.6 * subscriber.weight) + (1.8 * subscriber.height) - (4.7 * age)
        return bmr
    else:
        return None

def calculate_caloric_need(subscriber):
    bmr = calculate_bmr(subscriber)
    if bmr is None:
        return None
    activity_multiplier = {
        'Sedentary': 1.2,
        'Lightly Active': 1.375,
        'Moderately Active': 1.55,
        'Very Active': 1.725,
        'Extra Active': 1.9
    }
    multiplier = activity_multiplier.get(subscriber.activity_level, 1.2)
    caloric_need = bmr * multiplier
    return caloric_need

def load_subscriber_meals_for_date(subscriber, date):
    from flaskr.models import Meal
    meals = Meal.query.filter_by(diary_id=subscriber.diary_id).all()
    return [meal for meal in meals if meal.meal_time.date() == date] # This needs work as meal_time is not just date

def aggregate_meal_nutrition(meals):
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_sugar = 0
    total_fibre = 0
    for meal in meals:
        for item in meal.items:
            weight_grams = item.weight
            food = item.food
            total_calories += (food.kcal / 100) * weight_grams
            total_protein += (food.protein / 100) * weight_grams
            total_carbs += (food.carbs / 100) * weight_grams
            total_fat += (food.fats / 100) * weight_grams
            total_sugar += (food.sugar / 100) * weight_grams
            total_fibre += (food.fibre / 100) * weight_grams
    return {
        'calories': total_calories,
        'protein': total_protein,
        'carbs': total_carbs,
        'fat': total_fat,
        'sugar': total_sugar,
        'fibre': total_fibre,
    }

def update_nutrition_score(subscriber, date):
    from flaskr.models import NutritionScore
    meals = load_subscriber_meals_for_date(subscriber, date)
    nutrition_data = aggregate_meal_nutrition(meals)
    nutrition_score, calorie_score, macro_score = calculate_daily_score(meals, nutrition_data, subscriber)
    NutritionScore.create_new_score(subscriber.subscriber_id, date, nutrition_score, calorie_score, macro_score)
    return nutrition_score