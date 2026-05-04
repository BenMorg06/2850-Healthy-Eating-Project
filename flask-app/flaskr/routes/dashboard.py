from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from flaskr import db
# from flaskr.models import MealLog  # remove this hard import

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # ...existing code...
    return render_template("dashboard.html")

@dashboard_bp.route("/api/dashboard/weekly-metrics")
@login_required
def weekly_metrics():
    # Alex's code - start
    # NHS daily guideline values (general adult guidance).
    nhs_daily_targets = {
        "calories": 2000,  # kcal
        "fat": 70,         # g
        "carbs": 260,      # g
        "protein": 50      # g
    }

    labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Build current Monday-Sunday week window.
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Try to locate your real meal log model dynamically.
    # Replace with your exact model once confirmed.
    from flaskr import models
    LogModel = (
        getattr(models, "MealLog", None)
        or getattr(models, "FoodLog", None)
        or getattr(models, "DiaryEntry", None)
        or getattr(models, "IntakeLog", None)
    )

    # Default empty weekly series so frontend always renders.
    series = {
        "calories": [0.0] * 7,
        "fat": [0.0] * 7,
        "protein": [0.0] * 7,
        "carbs": [0.0] * 7,
    }

    if LogModel is not None:
        # Adjust these field names if your model uses different names.
        rows = (
            db.session.query(
                func.date(LogModel.logged_at).label("day"),
                func.coalesce(func.sum(LogModel.calories), 0).label("calories"),
                func.coalesce(func.sum(LogModel.fat), 0).label("fat"),
                func.coalesce(func.sum(LogModel.protein), 0).label("protein"),
                func.coalesce(func.sum(LogModel.carbs), 0).label("carbs"),
            )
            .filter(
                LogModel.user_id == current_user.id,
                LogModel.logged_at >= datetime.combine(week_start, datetime.min.time()),
                LogModel.logged_at < datetime.combine(week_end + timedelta(days=1), datetime.min.time()),
            )
            .group_by(func.date(LogModel.logged_at))
            .all()
        )

        days = {}
        for i in range(7):
            d = week_start + timedelta(days=i)
            days[d.isoformat()] = {"calories": 0.0, "fat": 0.0, "protein": 0.0, "carbs": 0.0}

        for row in rows:
            days[str(row.day)] = {
                "calories": float(row.calories or 0),
                "fat": float(row.fat or 0),
                "protein": float(row.protein or 0),
                "carbs": float(row.carbs or 0),
            }

        date_keys = [(week_start + timedelta(days=i)).isoformat() for i in range(7)]
        series = {
            "calories": [days[d]["calories"] for d in date_keys],
            "fat": [days[d]["fat"] for d in date_keys],
            "protein": [days[d]["protein"] for d in date_keys],
            "carbs": [days[d]["carbs"] for d in date_keys],
        }

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
    })
    # Alex's code - end