from __future__ import annotations

from uuid import uuid4

from flask import Blueprint, flash, redirect, request, url_for

from ..db import execute, fetch_one
from ..helpers import calculate_nutrition, login_required, today_str
from ..services import current_user, find_food_by_name, get_food

food_bp = Blueprint('food', __name__)


@food_bp.post('/toggle-favourite/<food_id>')
@login_required
def toggle_favourite(food_id: str):
    user = current_user()
    favourite = fetch_one('SELECT 1 FROM favourites WHERE user_id = ? AND food_id = ?', (user['id'], food_id))
    if favourite:
        execute('DELETE FROM favourites WHERE user_id = ? AND food_id = ?', (user['id'], food_id))
    else:
        execute('INSERT INTO favourites (user_id, food_id) VALUES (?, ?)', (user['id'], food_id))
    return redirect(request.referrer or url_for('main.home', page='menu'))


@food_bp.post('/food-lookup')
@login_required
def food_lookup():
    name = request.form.get('food_name', '').strip()
    grams_text = request.form.get('grams', '').strip()
    lookup_date = request.form.get('date', today_str())
    page = request.form.get('page', 'menu')

    if not name or not grams_text:
        result = 'Please enter both food name and grams.'
        return redirect(url_for('main.home', page=page, entry_mode='lookup', food_lookup_result=result, diary_date=lookup_date, professional_date=lookup_date))

    food = find_food_by_name(name)
    if not food:
        result = 'Food not found in database. Please use Manual Recipe Entry to enter your own recipe and nutrition values.'
        return redirect(url_for('main.home', page=page, entry_mode='lookup', food_lookup_result=result, diary_date=lookup_date, professional_date=lookup_date))

    nutrition = calculate_nutrition(dict(food), float(grams_text))
    result = f"Found: {food['name']} | {grams_text} g | {nutrition['calories']} kcal | Protein {nutrition['protein']} g | Carbs {nutrition['carbs']} g | Fat {nutrition['fat']} g"
    return redirect(url_for('main.home', page=page, entry_mode='lookup', food_lookup_result=result, diary_date=lookup_date, professional_date=lookup_date))


@food_bp.post('/add-food')
@login_required
def add_food():
    user = current_user()
    name = request.form.get('food_name', '').strip()
    grams = float(request.form.get('grams', '0') or 0)
    record_date = request.form.get('date', today_str())
    food = find_food_by_name(name)
    if not food or grams <= 0:
        flash('Food not found or grams invalid. Please use Manual Recipe Entry when needed.', 'error')
        return redirect(url_for('main.home', page='menu', entry_mode='lookup'))

    nutrition = calculate_nutrition(dict(food), grams)
    execute(
        """
        INSERT INTO diary_records
        (id, client_id, date, type, food_id, name, grams, calories, protein, carbs, fat, category, img, ingredients)
        VALUES (?, ?, ?, 'database', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            str(uuid4()), user['id'], record_date, food['id'], food['name'], grams,
            nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat'],
            food['category'], food['img'],
        ),
    )
    flash('Food record added successfully.', 'success')
    return redirect(url_for('main.home', page='menu', diary_date=record_date, professional_date=record_date))


@food_bp.post('/save-recipe')
@login_required
def save_recipe():
    user = current_user()
    record_date = request.form.get('date', today_str())
    name = request.form.get('name', '').strip()
    grams = float(request.form.get('grams', '0') or 0)
    category = request.form.get('category', '').strip() or 'Manual Recipe'
    ingredients = request.form.get('ingredients', '').strip()
    calories = float(request.form.get('calories', '0') or 0)
    protein = float(request.form.get('protein', '0') or 0)
    carbs = float(request.form.get('carbs', '0') or 0)
    fat = float(request.form.get('fat', '0') or 0)

    if not all([name, grams > 0, ingredients, calories >= 0, protein >= 0, carbs >= 0, fat >= 0]):
        flash('Please complete all manual recipe fields.', 'error')
        return redirect(url_for('main.home', page='menu', entry_mode='manual'))

    execute(
        """
        INSERT INTO diary_records
        (id, client_id, date, type, food_id, name, grams, calories, protein, carbs, fat, category, img, ingredients)
        VALUES (?, ?, ?, 'manual', NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid4()), user['id'], record_date, name, grams, calories, protein, carbs, fat,
            category, f"https://picsum.photos/seed/{name.replace(' ', '%20')}/300/200", ingredients,
        ),
    )
    flash('Manual recipe saved successfully.', 'success')
    return redirect(url_for('main.home', page='menu', entry_mode='manual', diary_date=record_date, professional_date=record_date))


@food_bp.post('/quick-add/<food_id>')
@login_required
def quick_add(food_id: str):
    user = current_user()
    food = get_food(food_id)
    grams = float(request.form.get('grams', '0') or 0)
    record_date = request.form.get('date', today_str())
    page = request.form.get('page', 'menu')
    if not food or grams <= 0:
        flash('Please enter valid grams.', 'error')
        return redirect(url_for('main.home', page=page, quick_add_food_id=food_id))
    nutrition = calculate_nutrition(dict(food), grams)
    execute(
        """
        INSERT INTO diary_records
        (id, client_id, date, type, food_id, name, grams, calories, protein, carbs, fat, category, img, ingredients)
        VALUES (?, ?, ?, 'database', ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            str(uuid4()), user['id'], record_date, food['id'], food['name'], grams,
            nutrition['calories'], nutrition['protein'], nutrition['carbs'], nutrition['fat'],
            food['category'], food['img'],
        ),
    )
    flash('Food added to diary.', 'success')
    return redirect(url_for('main.home', page=page, diary_date=record_date, professional_date=record_date))
