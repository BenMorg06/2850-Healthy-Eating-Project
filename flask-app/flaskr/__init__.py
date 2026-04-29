from datetime import datetime
import os
from flask import Flask, abort, app, jsonify, render_template, request, session, redirect, url_for, flash
from rapidfuzz import process, fuzz
from flaskr.extensions import db
from flaskr.models import Comment, Food, MealItem, Subscriber, Meal, Professional, Manages

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
        from flaskr.auth import auth_bp
        app.register_blueprint(auth_bp)
        db.create_all()

    @app.before_request
    def check_login():
        # define routes that don't require login
        allowed_routes = ['auth.login', 'auth.logout', 'auth.register', 'static'] 
        
        # check if user is logged in, if the route they are accessign requires login then redirect to login page
        if 'user_id' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.login'))

    @app.route('/')
    def home():
        return dashboard()
    
    # esnure user is logged in to view homepage
    def get_current_subscriber():
        user_id = session.get('user_id')
        if not user_id:
            return None
        return db.session.get(Subscriber, user_id)

    def get_visible_meals(subscriber):
        if not subscriber:
            return []

        all_meals = db.session.query(Meal).filter_by(diary_id=subscriber.diary_id)\
                .order_by(Meal.meal_time.desc())\
                .all()
        return [m for m in all_meals if len(m.items) > 0]

    @app.route('/diary')
    def diary():
        client_id = request.args.get('client_id', type=int)

        if client_id is not None:
            if not session.get('is_professional'):
                abort(403)

            professional_id = session.get('user_id')
            relationship = Manages.query.filter_by(
                professional_id=professional_id,
                subscriber_id=client_id
            ).first()
            if not relationship:
                abort(403)

            subscriber = db.session.get(Subscriber, client_id)
            if not subscriber:
                abort(404)
        else:
            subscriber = get_current_subscriber()
            if not subscriber:
                return redirect(url_for('auth.login'))

        meals = get_visible_meals(subscriber)
        return render_template('diary.html', active_page='diary', meals=meals)

    @app.route('/grocery_list')
    def grocery_list():
        client_id = request.args.get('client_id', type=int)

        if client_id is not None:
            if not session.get('is_professional'):
                abort(403)

            professional_id = session.get('user_id')
            relationship = Manages.query.filter_by(
                professional_id=professional_id,
                subscriber_id=client_id
            ).first()
            if not relationship:
                abort(403)

            subscriber = db.session.get(Subscriber, client_id)
            if not subscriber:
                abort(404)
        else:
            subscriber = get_current_subscriber()
            if not subscriber:
                return redirect(url_for('auth.login'))

        meals = get_visible_meals(subscriber)
        return render_template('grocery_list.html', active_page='grocery_list', meals=meals)
    
    @app.route('/dashboard')
    def dashboard():
        if session.get('is_professional'):
            return redirect(url_for('professional_dashboard'))
        return render_template('dashboard.html')
    
    @app.route('/create_meal', methods=['GET'])
    def create_meal():
        # ensures user is logged in before creating meal
        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        meal = Meal.create_new_meal(subscriber.diary_id, meal_time=datetime.now())
        return redirect(url_for('edit_meal', meal_id=meal.meal_id))
    
    @app.route('/meal/<int:meal_id>/edit')
    def edit_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        items = MealItem.get_by_meal(meal_id)
        return render_template('create_meal.html', active_page='diary', meal=meal, items=items)

    @app.route('/meal/<int:meal_id>/search', methods=['GET'])
    def search_food(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify([])

        all_foods = Food.query.all()
        query_words = set(query.split())

        scored = []
        for food in all_foods:
            name_lower = food.food_name.lower()
            
            first_word = name_lower.split(',')[0].split()[0]

            base_score = max(
                fuzz.WRatio(query, name_lower),
                fuzz.token_sort_ratio(query, name_lower),
                fuzz.token_set_ratio(query, name_lower)
            ) # base score based on overall fuzzy match of query to name

            first_word_boost = 40 if any(w == first_word for w in query_words) else 0 # boost score if word in search is first word of result

            # add small boosts for any matching words
            word_matches = sum(1 for w in query_words if w in name_lower) #
            word_boost = (word_matches / len(query_words)) * 15

            # add base and all boosts for final score
            final_score = base_score + first_word_boost + word_boost
            scored.append((food, final_score))

        # order by score 
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [(food, score) for food, score in scored if score >= 60][:10] # return first 10 results with score >=60

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
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        food_id = request.form.get('food_id')
        weight = request.form.get('weight', type=float)
        if not food_id or weight <= 0:
            return jsonify({'error': 'Invalid input'}), 400
        
        meal_item = MealItem.create_new_meal_item(meal_id, food_id, weight)
        return redirect(url_for('edit_meal', meal_id=meal_id))
    
    @app.route('/meal/<int:meal_id>/remove_item/<int:item_id>', methods=['POST'])
    def remove_meal_item(meal_id, item_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        meal_item = db.session.get(MealItem, item_id) or abort(404)
        if meal_item.meal_id != meal_id:
            return jsonify({'error': 'Item does not belong to this meal'}), 400

        db.session.delete(meal_item)
        db.session.commit()
        return redirect(url_for('edit_meal', meal_id=meal_id))
    
    @app.route('/meal/<int:meal_id>/finish', methods=['POST'])
    def finish_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        flash ('Meal saved successfully!', 'success')
        return redirect(url_for('diary'))
    
    @app.route('/meal/<int:meal_id>/cancel', methods=['POST'])
    def cancel_meal(meal_id):
        meal = db.session.get(Meal,meal_id) or abort(404)
        meal.delete_meal()
        db.session.commit()
        return redirect(url_for('diary'))
    
    @app.route('/meal/<int:meal_id>/delete', methods=['POST'])
    def delete_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        # Ensure the meal belongs to the current subscriber
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
        meal.delete_meal()
        flash('Meal deleted successfully!', 'success')
        return redirect(url_for('diary'))
    
    @app.route('/meal/<int:meal_id>/view')
    def view_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403)
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


    @app.route('/professional_dashboard')
    def professional_dashboard():
        if not session.get('is_professional'):
            flash('Access denied. Professional account required.', 'error')
            return redirect(url_for('dashboard'))
        if session.get('is_professional'):
            professional_id = session.get('user_id')
        
        managed_relationships = Manages.query.filter_by(professional_id=professional_id).all()
        clients = [db.session.get(Subscriber, rel.subscriber_id) for rel in managed_relationships]
        
        return render_template('professional_dashboard.html', active_page='professional',clients=clients)

    @app.route('/invite_client', methods=['GET', 'POST'])
    def invite_client():
        # Check if user is logged in and is a professional
        if not session.get('user_id') or not session.get('is_professional'):
            flash('Access denied. Professional account required.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            client_email = request.form.get('client_email')
            existing_client = Subscriber.query.filter_by(email=client_email).first()
            if existing_client:
                Manages.create_management_relationship(professional_id=session['user_id'], subscriber_id=existing_client.subscriber_id)
                flash('This subscriber is now linked to your profile.', 'success')
                return redirect(url_for('professional_dashboard'))
            
            flash(f'No subscriber found with email {client_email}.', 'error')
            return redirect(url_for('invite_client'))
        
        return render_template('invite_client.html', active_page='professional')

    return app
