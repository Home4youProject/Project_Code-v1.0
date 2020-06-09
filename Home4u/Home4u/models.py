from datetime import datetime
from Home4u import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


stayed = db.Table('stayed',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('house_id', db.Integer, db.ForeignKey('house.id'), primary_key=True)
    )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.Integer(), nullable=True, unique=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    firstname = db.Column(db.String(20), nullable=True)
    surname = db.Column(db.String(20), nullable=True)
    sex = db.Column(db.String(8), nullable=True)
    reviews = db.Column(db.Integer, default=0)
    review_num = db.Column(db.Integer, default=0)
    selected_id = db.Column(db.Integer)
    report = db.Column(db.Integer)
    balance = db.Column(db.Float, nullable=True, default=0)
    selected_request = db.Column(db.Integer)
    identity = db.Column(db.String, default='user')
    admin = db.Column(db.Boolean, default=False)

    houses = db.relationship('House', secondary=stayed , lazy='subquery', backref=db.backref('has_stayed', lazy=True))


    def __repr__(self):
        return f"User({self.email}', '{self.password}')"




class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer = db.Column(db.Integer, nullable=False)
    recipient = db.Column(db.Integer(), nullable=False)
    stars = db.Column(db.String(1), nullable=False)
    comments = db.Column(db.String(200))
    type = db.Column(db.String(20))



class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_name = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(60), nullable=False)
    square_meters = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    house_type = db.Column(db.String(20), nullable=True)
    visitors = db.Column(db.Integer(), nullable=True)
    available_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    availability = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer())
    reviews = db.Column(db.Integer, default=0)
    review_num = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(20), nullable=False, default='default_house.png')

    def __repr__(self):
        return f"'{self.price}', '{self.id}'"

class HouseSelector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer())

    def __repr__(self):
        return f"'{self.id}', '{self.house_id}'"


class SearchInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(60), nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=True)
    guests = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return f"'{self.location}', '{self.arrival_date}', '{self.guests}'"

class Communication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer())
    auto_type = db.Column(db.String(120))
    select_type = db.Column(db.String(100))
    receiver = db.Column(db.String(50), nullable=False)
    message =  db.Column(db.String(150))


    def __repr__(self):
        return f"Comunication('{self.auto_type}')"

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    req_sender = db.Column(db.String(20))
    req_receiver = db.Column(db.Integer)
    req_house = db.Column(db.Integer)
    req_type = db.Column(db.String(10), default='pending')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.String(10))
    house_id = db.Column(db.Integer)
