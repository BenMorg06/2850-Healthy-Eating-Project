from datetime import datetime
import os
from rapidfuzz import process, fuzz
from flask import Flask, abort, jsonify, render_template, request, session, redirect, url_for, flash
from flaskr.extensions import db
from flaskr.models import Comment, Food, MealItem, Subscriber, Meal

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)  # use init_app on the module-level db, not a new instance

    with app.app_context():
        from flaskr import models
        db.create_all()

    @app.route('/')
    def home():
        return render_template('base.html')
    
    @app.route('/diary')
    def diary():
        subscriber_id = 1 # for development, we will just use the first subscriber. In production, this should come from the session or authentication system.
        if not subscriber_id:
            return redirect(url_for('dashboard'))
        
        subscriber = db.session.get(Subscriber, subscriber_id)
        all_meals = db.session.query(Meal).filter_by(diary_id=subscriber.diary_id)\
                .order_by(Meal.meal_time.desc())\
                .all()
        meals = [m for m in all_meals if len(m.items) > 0]
        return render_template('diary.html', active_page='diary', meals=meals)
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/create_meal', methods=['GET'])
    def create_meal():
        subscriber_id = 1
        subscriber = db.session.get(Subscriber, subscriber_id)

        meal = Meal.create_new_meal(subscriber.diary_id, meal_time=datetime.now())
        return redirect(url_for('edit_meal', meal_id=meal.meal_id))
    
    @app.route('/meal/<int:meal_id>/edit')
    def edit_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        items = MealItem.get_by_meal(meal_id)
        return render_template('create_meal.html', active_page='diary', meal=meal, items=items)

    @app.route('/meal/<int:meal_id>/search', methods=['GET'])
    def search_food(meal_id):
        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify([])

        all_foods = Food.query.all()
        query_words = set(query.split())

        scored = []
        for food in all_foods:
            name_lower = food.food_name.lower()
            
            # First word of the food name e.g. "Salmon" from "Salmon, smoked, hot-smoked"
            first_word = name_lower.split(',')[0].split()[0]

            base_score = max(
                fuzz.WRatio(query, name_lower),
                fuzz.token_sort_ratio(query, name_lower),
                fuzz.token_set_ratio(query, name_lower)
            )

            # Strong boost if any query word matches the first word of the food name
            first_word_boost = 40 if any(w == first_word for w in query_words) else 0

            # Smaller boost if all query words appear anywhere in the name
            word_matches = sum(1 for w in query_words if w in name_lower)
            word_boost = (word_matches / len(query_words)) * 15

            final_score = base_score + first_word_boost + word_boost
            scored.append((food, final_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = [(food, score) for food, score in scored if score >= 40][:10]

        return jsonify([{
            'food_id':   food.food_id,
            'food_name': food.food_name,
            'kcal':      food.kcal,
            'protein':   food.protein,
            'carbs':     food.carbs,
            'fats':      food.fats,
            'score':     round(score, 1)
        } for food, score in top])

    @app.route('/meal/<int:meal_id>/add_item', methods=['POST'])
    def add_meal_item(meal_id):
        food_id = request.form.get('food_id')
        weight = request.form.get('weight', type=float)
        if not food_id or weight <= 0:
            return jsonify({'error': 'Invalid input'}), 400
        
        meal_item = MealItem.create_new_meal_item(meal_id, food_id, weight)
        return redirect(url_for('edit_meal', meal_id=meal_id))
    
    @app.route('/meal/<int:meal_id>/remove_item/<int:item_id>', methods=['POST'])
    def remove_meal_item(meal_id, item_id):
        meal_item = db.session.get(MealItem, item_id) or abort(404)
        if meal_item.meal_id != meal_id:
            return jsonify({'error': 'Item does not belong to this meal'}), 400

        db.session.delete(meal_item)
        db.session.commit()
        return redirect(url_for('edit_meal', meal_id=meal_id))
    
    @app.route('/meal/<int:meal_id>/finish', methods=['POST'])
    def finish_meal(meal_id):
        flash ('Meal saved successfully!', 'success')
        return redirect(url_for('diary'))
    
    @app.route('/meal/<int:meal_id>/cancel', methods=['POST'])
    def cancel_meal(meal_id):
        meal = db.session.get(Meal,meal_id) or abort(404)
        meal.delete_meal()
        db.session.commit()
        return redirect(url_for('diary'))
    
    @app.route('/meal/<int:meal_id>/view')
    def view_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        items = MealItem.get_by_meal(meal_id)
        comments = Comment.get_by_meal(meal_id)
        
        total_kcal    = round(sum((i.food.kcal     / 100) * i.weight for i in items), 1)
        total_protein = round(sum((i.food.protein  / 100) * i.weight for i in items), 1)
        total_carbs   = round(sum((i.food.carbs    / 100) * i.weight for i in items), 1)
        total_fat     = round(sum((i.food.fats     / 100) * i.weight for i in items), 1)

        daily_goal    = 2000
        kcal_pct      = min(round((total_kcal / daily_goal) * 100), 100)

        return render_template('meal_view.html',
            active_page='diary',
            meal=meal,
            items=items,
            comments=comments,
            total_kcal=total_kcal,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            daily_goal=daily_goal,
            kcal_pct=kcal_pct
        )   

    return app