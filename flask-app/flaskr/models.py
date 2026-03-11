from flaskr import db

class Subscriber(db.Model):
    subscriber_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pswd_hash = db.Column(db.String(128), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    # diary_id = db.Column(db.Integer, db.ForeignKey('FoodDiary.diary_id'), nullable=False)
