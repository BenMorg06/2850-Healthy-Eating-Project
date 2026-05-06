
from datetime import date

def calculate_daily_score(meals, nutrition_data, subscriber):
    '''
    Calorie Score: (Actual Calories / Caloric Need) * 100, capped at 150%
    Macro Score: Average of carbs/protein/fat/sugar scores
    - Carbs/Protein/Fat: Based on middle % of caloric_need
    - Excess fat penalized
    - Sugar penalized if >50g
    '''
    caloric_need = calculate_caloric_need(subscriber)
    if caloric_need is None or nutrition_data['calories'] == 0:
        return 0, 0, 0
    
    # Calorie score with penalty for excess
    actual_cal = nutrition_data['calories']
    if actual_cal <= caloric_need:
        calorie_score = (actual_cal / caloric_need) * 100
    else:
        calorie_score = max(0, 200 - (actual_cal / caloric_need) * 100)  # Penalty for overeating
    
    # Macro targets: middle of ranges * caloric_need
    macro_targets_pct = {
        'carbs': 55,    # middle of 45-65
        'protein': 17.5, # middle of 10-35
        'fat': 27.5     # middle of 20-35
    }
    
    macro_scores = []
    for macro, mid_pct in macro_targets_pct.items():
        target_cal = (mid_pct / 100) * caloric_need
        grams_per_cal = {'carbs': 4, 'protein': 4, 'fat': 9}[macro]
        target_grams = target_cal / grams_per_cal
        
        actual_grams = nutrition_data[macro]
        excess_ratio = (actual_grams - target_grams) / target_grams if target_grams > 0 else 0
        if excess_ratio > 0:
            score = max(0, 100 - (excess_ratio * 50))
        else:
            score = (actual_grams / target_grams) * 100 if target_grams > 0 else 0
        macro_scores.append(score)
    
    # Sugar penalty: max 50g recommended
    sugar_limit = 50
    actual_sugar = nutrition_data['sugar']
    if actual_sugar > sugar_limit:
        sugar_penalty = min(50, (actual_sugar - sugar_limit) / sugar_limit * 50)  # Up to 50 points penalty
        macro_scores.append(max(0, 100 - sugar_penalty))
    else:
        macro_scores.append(100)
    
    macro_score = sum(macro_scores) / len(macro_scores)
    nutrition_score = 0.5 * calorie_score + 0.5 * macro_score  # Equal weight
    return round(nutrition_score, 1), round(calorie_score, 1), round(macro_score, 1)

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