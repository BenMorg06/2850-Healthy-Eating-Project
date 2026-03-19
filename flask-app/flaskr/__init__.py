from datetime import datetime
import os
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flaskr.extensions import db
from flaskr.models import Food, MealItem, Subscriber, Meal

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
        
        subscriber = Subscriber.query.get(subscriber_id)
        meals = Meal.get_by_diary_id(subscriber.diary_id)
        return render_template('diary.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/create_meal', methods=['GET'])
    def create_meal():
        subscriber_id = 1
        subscriber = Subscriber.query.get(subscriber_id)

        meal = Meal.create_new_meal(subscriber.diary_id, meal_time=datetime.now())
        return redirect(url_for('edit_meal', meal_id=meal.meal_id))
    
    @app.route('/meal/<int:meal_id>/edit')
    def edit_meal(meal_id):
        meal = Meal.query.get_or_404(meal_id)
        items = MealItem.get_by_meal(meal_id)
        return render_template('create_meal.html', active_page='diary', meal=meal, items=items)
    
    @app.route('/meal/<int:meal_id>/search', methods=['GET'])
    def search_food(meal_id):
        query = request.args.get('q', '').strip()
        if query:
            results = Food.query.filter(Food.name.ilike(f'%{query}%')).all()
        return jsonify([food.to_dict() for food in results])

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
        meal_item = MealItem.query.get_or_404(item_id)
        if meal_item.meal_id != meal_id:
            return jsonify({'error': 'Item does not belong to this meal'}), 400

        db.session.delete(meal_item)
        db.session.commit()
        return redirect(url_for('edit_meal', meal_id=meal_id))
    
    @app.route('/meal/<int:meal_id>/finish', methods=['POST'])
    def finish_meal(meal_id):
        return redirect(url_for('diary'))

    return app