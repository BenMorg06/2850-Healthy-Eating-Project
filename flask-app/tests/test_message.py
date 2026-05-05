import pytest
from flaskr import create_app
from flaskr.extensions import db
from flaskr.models import Message, Professional, Subscriber, Manages
from datetime import date, datetime
from werkzeug.security import generate_password_hash

