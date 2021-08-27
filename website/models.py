from enum import IntFlag, unique
from re import X
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    pictureURL = db.Column(db.String(1000))
    numServings = db.Column(db.Integer)
    servingSize = db.Column(db.String(150))
    cookTime = db.Column(db.String(10))
    prepTime = db.Column(db.String(10))
    cookTemp = db.Column(db.String(5))
    notionID = db.Column(db.String(50), unique=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    recipe = db.relationship('Recipe', backref='dish', passive_deletes=True)
    steps = db.relationship('Steps', backref='dish', passive_deletes=True)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.String(10))
    measurement = db.Column(db.String(50))
    ing = db.Column(db.String(150))
    notes = db.Column(db.String(250), nullable=True)
    fat_total = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    fat_sat = db.Column(db.Integer, nullable=True)
    fat_trans = db.Column(db.Integer, nullable=True)
    cholesterol = db.Column(db.Integer, nullable=True)
    sodium = db.Column(db.Integer, nullable=True)
    potassium = db.Column(db.Integer, nullable=True)
    carb_total = db.Column(db.Integer, nullable=True)
    carb_fiber = db.Column(db.Integer, nullable=True)
    carb_sugar = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Integer, nullable=True)
    servsize = db.Column(db.String(100), nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    calories_fat = db.Column(db.Integer, nullable=True)
    pictureURL = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    dishfk = db.Column(db.Integer, db.ForeignKey(
        'dish.id', ondelete="CASCADE"), nullable=False)

class Steps(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    step_num = db.Column(db.Integer)
    step_text = db.Column(db.Text)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())    
    dishfk = db.Column(db.Integer, db.ForeignKey(
        'dish.id', ondelete="CASCADE"), nullable=False)