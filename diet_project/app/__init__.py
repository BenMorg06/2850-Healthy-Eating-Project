from flask import Flask

from .config import Config
from .db import close_db
from .helpers import round1
from .services import init_db
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.food import food_bp
from .routes.notes import notes_bp


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)
    app.add_template_filter(round1, 'round1')

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(notes_bp)

    with app.app_context():
        init_db()

    return app
