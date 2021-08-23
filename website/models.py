from enum import IntFlag, unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    pictureURL = db.Column(db.String(500))
    
    notionID = db.Column(db.String(50), unique=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.String(10))
    measurement = db.Column(db.String(50))
    ing = db.Column(db.String(150))
    notes = db.Column(db.String(250), nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
