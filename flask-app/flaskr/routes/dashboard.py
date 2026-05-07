from datetime import date, datetime, timedelta
from flask import Blueprint, abort, flash, render_template, jsonify, session
from flask_login import login_required
from flaskr.models import Subscriber, Meal

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/dashboard/weekly-metrics")
def weekly_metrics(client_id=None):
    # NHS daily guideline values (general adult guidance).
    nhs_daily_targets = {
        "calories": 2000,  # kcal
        "fat": 70,         # g
        "carbs": 260,      # g
        "protein": 50      # g
    }

    labels = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    ]

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    if session.get("is_professional"):
        if client_id is None:
            abort(400)
        professional_id = session.get('user_id')
        relationship = Manages.query.filter_by(
            professional_id=professional_id,
            subscriber_id=client_id
        ).first()
        if not relationship:
            abort(403)
        subscriber = Subscriber.query.get(client_id)
        if not subscriber:
            abort(404)
    else:
        subscriber_id = session.get("user_id")
        if subscriber_id is None:
            flash("Subscriber not found.", "error")
            return jsonify({"error": "Subscriber not found"}), 404
        subscriber = Subscriber.query.get(subscriber_id)
    if not subscriber or not subscriber.diary_id:
        series = {k: [0.0] * 7 for k in nhs_daily_targets}
        streak = 0
    else:
        week_data = {
            day.isoformat(): {
                "calories": 0.0,
                "fat": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
            }
            for day in (week_start + timedelta(days=i) for i in range(7))
        }

        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(
            week_end + timedelta(days=1), datetime.min.time()
        )

        meals = (
            Meal.query
            .filter_by(diary_id=subscriber.diary_id)
            .filter(Meal.meal_time >= week_start_dt)
            .filter(Meal.meal_time < week_end_dt)
            .all()
        )

        streak_start_dt = datetime.combine(
            today - timedelta(days=30), datetime.min.time()
        )
        streak_end_dt = datetime.combine(today, datetime.max.time())

        streak_meals = (
            Meal.query
            .filter_by(diary_id=subscriber.diary_id)
            .filter(Meal.meal_time >= streak_start_dt)
            .filter(Meal.meal_time <= streak_end_dt)
            .all()
        )

        streak_dates = {meal.meal_time.date() for meal in streak_meals}

        for meal in meals:
            day_key = meal.meal_time.date().isoformat()
            if day_key not in week_data:
                continue

            for item in meal.items:
                if not item.food:
                    continue

                weight = float(item.weight or 0)
                week_data[day_key]["calories"] += (
                    (item.food.kcal or 0) * weight / 100
                )
                week_data[day_key]["fat"] += (
                    (item.food.fats or 0) * weight / 100
                )
                week_data[day_key]["protein"] += (
                    (item.food.protein or 0) * weight / 100
                )
                week_data[day_key]["carbs"] += (
                    (item.food.carbs or 0) * weight / 100
                )

        def week_series(key):
            return [
                round(
                    week_data[
                        (week_start + timedelta(days=i)).isoformat()
                    ][key],
                    1
                )
                for i in range(7)
            ]

        series = {
            "calories": week_series("calories"),
            "fat":      week_series("fat"),
            "protein":  week_series("protein"),
            "carbs":    week_series("carbs"),
        }

        start_day = today if today in streak_dates else today - timedelta(days=1)
        streak = 0
        current_day = start_day
        while current_day in streak_dates:
            streak += 1
            current_day -= timedelta(days=1)

    totals = {k: sum(v) for k, v in series.items()}
    weekly_targets = {k: v * 7 for k, v in nhs_daily_targets.items()}
    percentages = {
        k: round((totals[k] / weekly_targets[k]) * 100, 1)
        if weekly_targets[k] else 0
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
