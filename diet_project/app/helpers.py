from __future__ import annotations

from datetime import date
from functools import wraps
from typing import Any, Callable

from flask import flash, redirect, request, session, url_for


def round1(value: float | int) -> float:
    return round(float(value), 1)


def today_str() -> str:
    return date.today().isoformat()


def calculate_nutrition(food: dict[str, Any], grams: float) -> dict[str, float]:
    factor = grams / 100
    return {
        'calories': round(food['calories'] * factor, 1),
        'protein': round(food['protein'] * factor, 1),
        'carbs': round(food['carbs'] * factor, 1),
        'fat': round(food['fat'] * factor, 1),
    }


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped_view(*args: Any, **kwargs: Any) -> Any:
        if not session.get('user_id'):
            flash('Please log in first.', 'error')
            return redirect(url_for('auth.auth_page', tab='login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view
