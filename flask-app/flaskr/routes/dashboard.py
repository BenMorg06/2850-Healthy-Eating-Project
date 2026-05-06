from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from flaskr.extensions import db
from flaskr.models import Subscriber, Meal, MealItem

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # ...existing code...
    return render_template("dashboard.html")

@dashboard_bp.route("/api/dashboard/weekly-metrics")
def weekly_metrics():
    # NHS daily guideline values (general adult guidance).
    nhs_daily_targets = {
        "calories": 2000,  # kcal
        "fat": 70,         # g
        "carbs": 260,      # g
        "protein": 50      # g
    }

    labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    subscriber_id = None
    if hasattr(current_user, 'id') and current_user.is_authenticated:
        subscriber_id = getattr(current_user, 'subscriber_id', None) or current_user.id

    if subscriber_id is None:
        subscriber_id = 1

    subscriber = Subscriber.query.get(subscriber_id)
    if not subscriber or not subscriber.diary_id:
        series = {k: [0.0] * 7 for k in nhs_daily_targets}
        streak = 0
    else:
        week_data = {
            day.isoformat(): {"calories": 0.0, "fat": 0.0, "protein": 0.0, "carbs": 0.0}
            for day in (week_start + timedelta(days=i) for i in range(7))
        }

        meals = (
            Meal.query
            .filter_by(diary_id=subscriber.diary_id)
            .filter(Meal.meal_time >= datetime.combine(week_start, datetime.min.time()))
            .filter(Meal.meal_time < datetime.combine(week_end + timedelta(days=1), datetime.min.time()))
            .all()
        )

        streak_meals = (
            Meal.query
            .filter_by(diary_id=subscriber.diary_id)
            .filter(Meal.meal_time >= datetime.combine(today - timedelta(days=30), datetime.min.time()))
            .filter(Meal.meal_time <= datetime.combine(today, datetime.max.time()))
            .all()
        )

        streak_dates = {meal.meal_time.date() for meal in streak_meals}

        meal_dates = set()
        for meal in meals:
            day_key = meal.meal_time.date().isoformat()
            if day_key not in week_data:
                continue
            meal_dates.add(meal.meal_time.date())

            for item in meal.items:
                if not item.food:
                    continue

                weight = float(item.weight or 0)
                week_data[day_key]["calories"] += (item.food.kcal or 0) * weight / 100
                week_data[day_key]["fat"] += (item.food.fats or 0) * weight / 100
                week_data[day_key]["protein"] += (item.food.protein or 0) * weight / 100
                week_data[day_key]["carbs"] += (item.food.carbs or 0) * weight / 100

        series = {
            "calories": [round(week_data[(week_start + timedelta(days=i)).isoformat()]["calories"], 1) for i in range(7)],
            "fat": [round(week_data[(week_start + timedelta(days=i)).isoformat()]["fat"], 1) for i in range(7)],
            "protein": [round(week_data[(week_start + timedelta(days=i)).isoformat()]["protein"], 1) for i in range(7)],
            "carbs": [round(week_data[(week_start + timedelta(days=i)).isoformat()]["carbs"], 1) for i in range(7)]
        }

        streak = 0
        current_day = today
        while current_day in streak_dates:
            streak += 1
            current_day -= timedelta(days=1)

    totals = {k: sum(v) for k, v in series.items()}
    weekly_targets = {k: v * 7 for k, v in nhs_daily_targets.items()}
    percentages = {
        k: round((totals[k] / weekly_targets[k]) * 100, 1) if weekly_targets[k] else 0
        for k in totals
    }

    return jsonify({
        "labels": labels,
        "series": series,
        "percentages": percentages,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "streak": streak
    })