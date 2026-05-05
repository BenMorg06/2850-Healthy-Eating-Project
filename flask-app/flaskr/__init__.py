from datetime import date, datetime
import os
from flask import Flask, abort, app, jsonify, render_template, request, session, redirect, url_for, flash
from rapidfuzz import process, fuzz
from flaskr.models import Comment, Food, MealItem, Subscriber, Meal, Professional, Manages, SavedMeal, NutritionScore, Message
from flaskr.extensions import db, migrate
from flaskr.nutrition import calculate_caloric_need, load_subscriber_meals_for_date, aggregate_meal_nutrition, calculate_daily_score, save_nutrition_score

def create_app(test_config=None):
    # Base creation template adapted from Flask tutorial at https://flask.palletsprojects.com/en/2.3.x/tutorial/factory/
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SERVER_NAME=None # Used for ngrok to allow hosting & multidevice testing
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Ensure most recent database models loaded
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from flaskr import models
        from flaskr.auth import auth_bp
        app.register_blueprint(auth_bp)
        db.create_all()

    # Make sure subscribers and professionals are sent to log in first
    @app.before_request
    def check_login():
        allowed_routes = ['auth.login', 'auth.logout', 'auth.register', 'static']

        # check if user is logged in, if the route they are accessign requires login then redirect to login page
        if 'user_id' not in session and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.login'))

    def get_current_subscriber():
        if session.get('is_professional'):
            return None
        user_id = session.get('user_id')
        if not user_id:
            return None
        return db.session.get(Subscriber, user_id)

    def get_current_professional():
        user_id = session.get('user_id')
        if not user_id or not session.get('is_professional'):
            return None
        return db.session.get(Professional, user_id)

    def get_subscriber_macro_needs(caloric_need):
        if not caloric_need:
            return {}
        macro_targets_pct = {
            'carbs': 55,
            'protein': 17.5,
            'fat': 27.5
        }
        targets = {}
        # Use BMR & Caloric need calculations to build personalised macro targets for subscriber
        # Based on percentage guidelines from WHO 
        for macro, pct in macro_targets_pct.items():
            target_cal = (pct / 100) * caloric_need
            grams_per_cal = {'carbs': 4, 'protein': 4, 'fat': 9}[macro]
            targets[macro] = round(target_cal / grams_per_cal, 1)
        targets['sugar'] = 50   
        targets['fibre'] = 25   
        return targets
 

    def get_past_nutrition_scores(subscriber_id):
        # Return last 7 days of scores for subscriber
        recent_scores = (
            NutritionScore.query
            .filter_by(subscriber_id=subscriber_id)
            .order_by(NutritionScore.date.desc())
            .limit(7)
            .all()
        )
        recent_scores = list(reversed(recent_scores))
        return {
            'dates':  [s.date.strftime('%d %b') for s in recent_scores],
            'scores': [float(s.score) for s in recent_scores],
        }

    @app.route('/')
    def home():
        # By default send users to dashboard
        return dashboard()

    @app.route('/dashboard')
    def dashboard():
        # Based on user type (subscriber vs professional) either show subscriber dashboard or redirect to professional dashboard
        if session.get('is_professional'):
            return redirect(url_for('professional_dashboard'))

        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        caloric_need = calculate_caloric_need(subscriber)
        macro_targets = get_subscriber_macro_needs(caloric_need)

        # Load todays meals for subscriber to view 
        today = date.today()
        all_meals_today = load_subscriber_meals_for_date(subscriber, today)
        meals_today = [m for m in all_meals_today if len(m.items) > 0]

        # Calculate nutrition score and calorie info to display to subscriber on dashboard
        score, calorie_score, macro_score = None, None, None
        nutrition_data = {}
        caloric_intake = 0

        if meals_today:
            nutrition_data = aggregate_meal_nutrition(meals_today)
            caloric_intake = nutrition_data['calories']
            score, calorie_score, macro_score = calculate_daily_score(
                meals_today, nutrition_data, subscriber
            )
            # Create entry in NutritionScore tabel to save history and provide insight in future
            save_nutrition_score(subscriber.subscriber_id, today, score, calorie_score, macro_score)

        # Fetch last 7 days of score for the weekly graph
        score_history = get_past_nutrition_scores(subscriber.subscriber_id)

        return render_template(
            'dashboard.html',
            caloric_need=caloric_need,
            caloric_intake=caloric_intake,
            score=score,
            calorie_score=calorie_score,
            macro_targets=macro_targets,
            macro_score=macro_score,
            nutrition_data=nutrition_data,
            score_history=score_history,
        )

    @app.route('/diary')
    def diary():
        # Page for Subscribers to see all their logged meals
        # Also used for professionals to see their clients meals
        client_id = request.args.get('client_id', type=int)

        if client_id is not None:
            if not session.get('is_professional'):
                abort(403, 'Professional account required to view client diaries.')

            professional_id = session.get('user_id')
            relationship = Manages.query.filter_by(
                professional_id=professional_id,
                subscriber_id=client_id
            ).first()
            if not relationship:
                abort(403, 'Client not managed by this professional')

            subscriber = db.session.get(Subscriber, client_id)
            if not subscriber:
                abort(404)
        else:
            subscriber = get_current_subscriber()
            if not subscriber:
                return redirect(url_for('auth.login'))

        all_meals = (db.session.query(Meal).filter_by(diary_id=subscriber.diary_id)\
            .order_by(Meal.meal_time.desc())\
            .all()
        )
        meals = [m for m in all_meals if len(m.items) > 0]

        return render_template('diary.html', active_page='diary', meals=meals)

    @app.route('/create_meal', methods=['GET'])
    def create_meal():
        # Allows subscribers to create new meals
        # ensures user is logged in before creating meal
        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        meal = Meal.create_new_meal(subscriber.diary_id, meal_time=datetime.now())
        return redirect(url_for('edit_meal', meal_id=meal.meal_id))

    @app.route('/meal/<int:meal_id>/edit')
    def edit_meal(meal_id):
        # Page for subscribers to edit meals
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')
        items = MealItem.get_by_meal(meal_id)
        return render_template('create_meal.html', active_page='diary', meal=meal, items=items)

    @app.route('/meal/<int:meal_id>/search', methods=['GET'])
    def search_food(meal_id):
        # Subscribers can use fuzzy search to find foods to add to their meals
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')

        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify([])

        all_foods = Food.query.all()
        query_words = set(query.split())

        scored = []
        # Fuzzy search algorithm based on combination of first word matchhing, overall string similarity, and number of query words appearing in the food name
        # We experimented with different approaches and this combination seemed to provide good results in testing
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
        # Allows subscribers to add food items to meals with specified weight
        meal = db.session.get(Meal, meal_id) or abort(404, 'Meal not found')
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')

        food_id = request.form.get('food_id')
        weight = request.form.get('weight', type=float)
        if not food_id or weight <= 0:
            return jsonify({'error': 'Invalid input'}), 400

        meal_item = MealItem.create_new_meal_item(meal_id, food_id, weight)
        return redirect(url_for('edit_meal', meal_id=meal_id))

    @app.route('/meal/<int:meal_id>/remove_item/<int:item_id>', methods=['POST'])
    def remove_meal_item(meal_id, item_id):
        # Allows subscribers to remove items from meals
        meal = db.session.get(Meal, meal_id) or abort(404, 'Meal not found')
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')

        meal_item = db.session.get(MealItem, item_id) or abort(404)
        if meal_item.meal_id != meal_id:
            return jsonify({'error': 'Item does not belong to this meal'}), 400

        db.session.delete(meal_item)
        db.session.commit()
        return redirect(url_for('edit_meal', meal_id=meal_id))

    @app.route('/meal/<int:meal_id>/finish', methods=['POST'])
    def finish_meal(meal_id):
        # When subscribers have finished adding to a meal they can confirm it and save it to their diary
        meal = db.session.get(Meal, meal_id) or abort(404, 'Meal not found')
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')
        flash ('Meal saved successfully!', 'success')
        return redirect(url_for('diary'))

    @app.route('/meal/<int:meal_id>/cancel', methods=['POST'])
    def cancel_meal(meal_id):
        # Allow subscriber to cancel meal creation which deletes the meal and all associated items
        meal = db.session.get(Meal, meal_id) or abort(404, 'Meal not found')
        meal.delete_meal()
        db.session.commit()
        return redirect(url_for('diary'))

    @app.route('/meal/<int:meal_id>/delete', methods=['POST'])
    def delete_meal(meal_id):
        # Users can delete meals from their diary and remove from favourites
        meal = db.session.get(Meal, meal_id) or abort(404)
        # Ensure the meal belongs to the current subscriber
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')
        meal.delete_meal()
        flash('Meal deleted successfully!', 'success')
        return redirect(url_for('diary'))

    @app.route('/meal/<int:meal_id>/favourite', methods=['POST'])
    def favourite_meal(meal_id):
        # Subscribers can favourite meals to easily find and log again in the future
        meal = db.session.get(Meal, meal_id) or abort(404, 'Meal not found')
        subscriber = get_current_subscriber()
        if not subscriber or meal.diary_id != subscriber.diary_id:
            abort(403, 'Access denied')

        meal_name = meal.meal_time.strftime('%d %b %Y – %H:%M')
        SavedMeal.create_new_saved_meal(subscriber.subscriber_id, meal_id, meal_name)
        flash('Meal added to favourites.', 'success')
        return redirect(url_for('diary'))

    @app.route('/favourites')
    def favourites():
        # Renders page showing all favourited meals for subscriber with option to quick add them to their diary
        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        saved_meals = SavedMeal.get_by_subscriber(subscriber.subscriber_id)
        return render_template('favourites.html', active_page='favourites', saved_meals=saved_meals)

    @app.route('/favourites/quick_add/<int:meal_id>', methods=['POST'])
    def quick_add_favourite_meal(meal_id):
        # Subscribers can quick log meals from their favourites
        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        saved = SavedMeal.query.filter_by(
            subscriber_id=subscriber.subscriber_id,
            meal_id=meal_id
        ).first()
        if not saved:
            abort(404, 'Favourite meal not found')

        source_meal = db.session.get(Meal, meal_id)
        if not source_meal:
            flash('Original meal no longer exists. Cannot quick add.', 'error')
            return redirect(url_for('favourites'))

        new_meal = Meal.create_new_meal(subscriber.diary_id, meal_time=datetime.now())
        for item in source_meal.items:
            MealItem.create_new_meal_item(new_meal.meal_id, item.food_id, item.weight)

        flash('Favourite meal added to your diary.', 'success')
        return redirect(url_for('diary'))

    @app.route('/meal/<int:meal_id>/view')
    def view_meal(meal_id):
        meal = db.session.get(Meal, meal_id) or abort(404)
        subscriber = get_current_subscriber()
        professional = get_current_professional()
        can_comment = False

        if subscriber:
            if meal.diary_id != subscriber.diary_id:
                abort(403)
        elif professional:
            meal_owner = Subscriber.query.filter_by(diary_id=meal.diary_id).first()
            if not meal_owner:
                abort(404)
            relationship = Manages.query.filter_by(
                professional_id=professional.professional_id,
                subscriber_id=meal_owner.subscriber_id
            ).first()
            if not relationship:
                abort(403)
            can_comment = True
        else:
            abort(403)

        items = MealItem.get_by_meal(meal_id)
        comments = Comment.get_by_meal(meal_id)

        total_kcal    = round(sum((i.food.kcal    / 100) * i.weight for i in items), 1)
        total_protein = round(sum((i.food.protein / 100) * i.weight for i in items), 1)
        total_carbs   = round(sum((i.food.carbs   / 100) * i.weight for i in items), 1)
        total_fat     = round(sum((i.food.fats    / 100) * i.weight for i in items), 1)

        daily_goal = 2000
        kcal_pct   = min(round((total_kcal / daily_goal) * 100), 100)

        return render_template(
            'meal_view.html',
            active_page='diary',
            meal=meal,
            items=items,
            comments=comments,
            total_kcal=total_kcal,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            daily_goal=daily_goal,
            kcal_pct=kcal_pct,
            can_comment=can_comment
        )

    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        # Subscribers can update settings that affect their nutrition score 
        # Height Weight Sex Activity Level
        if session.get('is_professional'):
            return redirect(url_for('professional_dashboard'))

        subscriber = get_current_subscriber()
        if not subscriber:
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            subscriber.height         = request.form.get('height', type=float)
            subscriber.weight         = request.form.get('weight', type=float)
            subscriber.sex            = request.form.get('sex')
            subscriber.activity_level = request.form.get('activity_level')
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings'))

        return render_template('settings.html', active_page='settings', subscriber=subscriber)

    @app.route('/meal/<int:meal_id>/comment', methods=['POST'])
    def add_comment(meal_id):
        professional = get_current_professional()
        if not professional:
            abort(403)

        meal = db.session.get(Meal, meal_id) or abort(404)
        meal_owner = Subscriber.query.filter_by(diary_id=meal.diary_id).first()
        if not meal_owner:
            abort(404)

        relationship = Manages.query.filter_by(
            professional_id=professional.professional_id,
            subscriber_id=meal_owner.subscriber_id
        ).first()
        if not relationship:
            abort(403)

        title = request.form.get('title', '').strip()
        body  = request.form.get('body',  '').strip()
        if not title or not body:
            flash('Title and comment body are required.', 'error')
            return redirect(url_for('view_meal', meal_id=meal_id))

        Comment.create_new_comment(meal_id, professional.professional_id, title, body)
        flash('Comment added successfully.', 'success')
        return redirect(url_for('view_meal', meal_id=meal_id))

    @app.route('/professional_dashboard')
    def professional_dashboard():
        if not session.get('is_professional'):
            flash('Access denied. Professional account required.', 'error')
            return redirect(url_for('dashboard'))

        professional_id = session.get('user_id')
        managed_relationships = Manages.query.filter_by(professional_id=professional_id).all()
        clients = [db.session.get(Subscriber, rel.subscriber_id) for rel in managed_relationships]

        return render_template(
            'professional_dashboard.html',
            active_page='professional',
            clients=clients,
        )

    @app.route('/client/<int:client_id>')
    def view_client(client_id):
        # Professionals can view their clients dashboard which shows their nutrition score, caloric intake, and meals for the day
        # Professionals can monitor their clients progress and provide support and advice as needed.
        if not session.get('is_professional'):
            abort(403)

        professional_id = session.get('user_id')
        relationship = Manages.query.filter_by(
            professional_id=professional_id,
            subscriber_id=client_id
        ).first()
        if not relationship:
            abort(403)

        client = db.session.get(Subscriber, client_id)
        if not client:
            abort(404)

        today = date.today()
        all_meals_today = load_subscriber_meals_for_date(client, today)
        meals_today = [m for m in all_meals_today if len(m.items) > 0]

        caloric_need = calculate_caloric_need(client)
        macro_targets = get_subscriber_macro_needs(caloric_need)
        score = calorie_score = macro_score = None
        nutrition_data = {}
        caloric_intake = 0

        if meals_today:
            nutrition_data = aggregate_meal_nutrition(meals_today)
            caloric_intake = nutrition_data['calories']
            score, calorie_score, macro_score = calculate_daily_score(
                meals_today, nutrition_data, client
            )
            # Persist score so history chart has data
            save_nutrition_score(client_id, today, score, calorie_score, macro_score)

        score_history = get_past_nutrition_scores(client_id)

        return render_template(
            'client_view.html',
            active_page='professional',
            client=client,
            caloric_need=caloric_need,
            caloric_intake=caloric_intake,
            score=score,
            calorie_score=calorie_score,
            macro_targets=macro_targets,
            macro_score=macro_score,
            nutrition_data=nutrition_data,
            today=today,
            score_history=score_history,
        )

    @app.route('/invite_client', methods=['GET', 'POST'])
    def invite_client():
        if not session.get('user_id') or not session.get('is_professional'):
            flash('Access denied. Professional account required.', 'error')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            client_email = request.form.get('client_email')
            existing_client = Subscriber.query.filter_by(email=client_email).first()
            if existing_client:
                Manages.create_management_relationship(
                    professional_id=session['user_id'],
                    subscriber_id=existing_client.subscriber_id
                )
                flash('This subscriber is now linked to your profile.', 'success')
                return redirect(url_for('professional_dashboard'))

            flash(f'No subscriber found with email {client_email}.', 'error')
            return redirect(url_for('invite_client'))

        return render_template('invite_client.html', active_page='professional')

    @app.route('/messages')
    def messages():
        if session.get('is_professional'):
            professional_id = session.get('user_id')
            subscriber_id = None
        else:
            professional_id = None
            subscriber_id = session.get('user_id')

        if not professional_id and not subscriber_id:
            return redirect(url_for('auth.login'))

        all_messages = Message.get_user_messages(professional_id, subscriber_id)

        conversations = {}
        for message in all_messages:
            if message.sender_professional_id == professional_id and message.sender_subscriber_id == subscriber_id:
                other_professional_id = message.recipient_professional_id
                other_subscriber_id = message.recipient_subscriber_id
            else:
                other_professional_id = message.sender_professional_id
                other_subscriber_id = message.sender_subscriber_id

            # Create conversation key
            conv_key = f"{other_professional_id or 0}_{other_subscriber_id or 0}"

            if conv_key not in conversations:
                if other_professional_id:
                    other_person = Professional.query.get(other_professional_id)
                    other_name = other_person.name if other_person else "Unknown Professional"
                else:
                    other_person = Subscriber.query.get(other_subscriber_id)
                    other_name = other_person.name if other_person else "Unknown Client"

                conversations[conv_key] = {
                    'other_professional_id': other_professional_id,
                    'other_subscriber_id': other_subscriber_id,
                    'other_name': other_name,
                    'last_message': message,
                    'unread_count': 0
                }

            # Count unread messages
            if not message.is_read and message.recipient_professional_id == professional_id and message.recipient_subscriber_id == subscriber_id:
                conversations[conv_key]['unread_count'] += 1

        # Sort conversations by last message time
        conversations = dict(sorted(conversations.items(), key=lambda x: x[1]['last_message'].sent_at, reverse=True))

        return render_template('messages.html', active_page='messages', conversations=conversations)

    @app.route('/messages/<int:other_professional_id>/<int:other_subscriber_id>')
    def view_conversation(other_professional_id, other_subscriber_id):
        other_professional_id = other_professional_id if other_professional_id != 0 else None
        other_subscriber_id = other_subscriber_id if other_subscriber_id != 0 else None

        if session.get('is_professional'):
            professional_id = session.get('user_id')
            subscriber_id = None
        else:
            professional_id = None
            subscriber_id = session.get('user_id')

        if not professional_id and not subscriber_id:
            return redirect(url_for('auth.login'))

        conversation_messages = Message.get_conversation(
            professional_id, subscriber_id,
            other_professional_id, other_subscriber_id
        )

        for message in conversation_messages:
            if message.recipient_professional_id == professional_id and message.recipient_subscriber_id == subscriber_id and not message.is_read:
                message.mark_as_read()

        if other_professional_id:
            other_person = db.session.get(Professional, other_professional_id)
            other_name = other_person.name if other_person else "Unknown Professional"
        else:
            other_person = db.session.get(Subscriber, other_subscriber_id)
            other_name = other_person.name if other_person else "Unknown Client"

        return render_template('conversation.html',
            active_page='messages',
            messages=conversation_messages,
            other_professional_id=other_professional_id,
            other_subscriber_id=other_subscriber_id,
            other_name=other_name
        )

    @app.route('/messages/send', methods=['POST'])
    def send_message():
        if session.get('is_professional'):
            sender_professional_id = session.get('user_id')
            sender_subscriber_id = None
        else:
            sender_professional_id = None
            sender_subscriber_id = session.get('user_id')

        if not sender_professional_id and not sender_subscriber_id:
            abort(403)

        recipient_professional_id = request.form.get('recipient_professional_id', type=int)
        recipient_subscriber_id = request.form.get('recipient_subscriber_id', type=int)
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()

        if not subject or not body:
            flash('Subject and message body are required.', 'error')
            return redirect(request.referrer or url_for('messages'))

        # Verify the recipient relationship (for professionals and clients)
        if sender_professional_id and recipient_subscriber_id:
            relationship = Manages.query.filter_by(
                professional_id=sender_professional_id,
                subscriber_id=recipient_subscriber_id
            ).first()
            if not relationship:
                abort(403)
        elif sender_subscriber_id and recipient_professional_id:
            relationship = Manages.query.filter_by(
                professional_id=recipient_professional_id,
                subscriber_id=sender_subscriber_id
            ).first()
            if not relationship:
                abort(403)

        Message.create_new_message(
            sender_professional_id, sender_subscriber_id,
            recipient_professional_id, recipient_subscriber_id,
            subject, body
        )

        flash('Message sent successfully.', 'success')
        return redirect(url_for('view_conversation',
            other_professional_id=recipient_professional_id or 0,
            other_subscriber_id=recipient_subscriber_id or 0
        ))

    @app.route('/messages/compose', methods=['GET', 'POST'])
    def compose_message():
        if session.get('is_professional'):
            sender_professional_id = session.get('user_id')
            sender_subscriber_id = None

            managed_relationships = Manages.query.filter_by(professional_id=sender_professional_id).all()
            recipients = [{'id': rel.subscriber_id, 'name': db.session.get(Subscriber, rel.subscriber_id).name, 'email': db.session.get(Subscriber, rel.subscriber_id).email, 'type': 'subscriber'} for rel in managed_relationships]
        else:
            sender_professional_id = None
            sender_subscriber_id = session.get('user_id')

            relationship = Manages.query.filter_by(subscriber_id=sender_subscriber_id).first()
            if relationship:
                professional = Professional.query.get(relationship.professional_id)
                recipients = [{'id': professional.professional_id, 'name': professional.name, 'email': professional.email, 'type': 'professional'}] if professional else []
            else:
                recipients = []

        if request.method == 'POST':
            recipient_type = request.form.get('recipient_type')
            recipient_id = request.form.get('recipient_id', type=int)
            subject = request.form.get('subject', '').strip()
            body = request.form.get('body', '').strip()

            if not recipient_type or not recipient_id or not subject or not body:
                flash('All fields are required.', 'error')
                return redirect(url_for('compose_message'))

            if recipient_type == 'subscriber':
                if not session.get('is_professional'):
                    abort(403)
                relationship = Manages.query.filter_by(
                    professional_id=sender_professional_id,
                    subscriber_id=recipient_id
                ).first()
                if not relationship:
                    abort(403)

                Message.create_new_message(
                    sender_professional_id, None,  
                    None, recipient_id, 
                    subject, body
                )
                return redirect(url_for('view_conversation', other_professional_id=0, other_subscriber_id=recipient_id))

            elif recipient_type == 'professional':
                # Subscriber sending to professional
                if session.get('is_professional'):
                    abort(403)
                # Verify relationship
                relationship = Manages.query.filter_by(
                    professional_id=recipient_id,
                    subscriber_id=sender_subscriber_id
                ).first()
                if not relationship:
                    abort(403)

                Message.create_new_message(
                    None, sender_subscriber_id,  
                    recipient_id, None,  
                    subject, body
                )
                return redirect(url_for('view_conversation', other_professional_id=recipient_id, other_subscriber_id=0))

            flash('Message sent successfully.', 'success')

        # Pre-fill recipient if specified in URL params
        prefill_recipient_professional_id = request.args.get('recipient_professional_id', type=int)
        prefill_recipient_subscriber_id = request.args.get('recipient_subscriber_id', type=int)

        prefill_recipient = None
        if prefill_recipient_professional_id and not session.get('is_professional'):
            prefill_recipient = Professional.query.get(prefill_recipient_professional_id)
            if prefill_recipient:
                relationship = Manages.query.filter_by(
                    professional_id=prefill_recipient_professional_id,
                    subscriber_id=sender_subscriber_id
                ).first()
                if not relationship:
                    prefill_recipient = None
        elif prefill_recipient_subscriber_id and session.get('is_professional'):
            prefill_recipient = Subscriber.query.get(prefill_recipient_subscriber_id)
            if prefill_recipient:
                relationship = Manages.query.filter_by(
                    professional_id=sender_professional_id,
                    subscriber_id=prefill_recipient_subscriber_id
                ).first()
                if not relationship:
                    prefill_recipient = None

        return render_template('compose_message.html',
            active_page='messages',
            recipients=recipients,
            prefill_recipient=prefill_recipient
        )

    return app