
from datetime import date

def calculate_daily_score(subscriber, date):
    return 'Daily Score - To be implemented'

def calculate_bmr(subscriber):
    age = subscriber.date_of_birth and (date.today().year - subscriber.date_of_birth.year)
    if age is None or subscriber.height is None or subscriber.weight is None or subscriber.sex is None:
        return None
    if subscriber.sex == 'Male':
        bmr = 66.5 + (13.75 * subscriber.weight) + (5 * subscriber.height) - (6.75 * subscriber.age)
        return bmr
    elif subscriber.sex == 'Female':
        bmr = 655.1 + (9.6 * subscriber.weight) + (1.8 * subscriber.height) - (4.7 * subscriber.age)
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
