from enum import IntFlag, unique
from operator import itemgetter
from re import X
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime

#Users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

#Guill Menu
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
    plan = db.relationship('Planner', backref='dish', passive_deletes=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.String(10))
    measurement = db.Column(db.String(50))
    ing = db.Column(db.String(150))
    catagory = db.Column(db.String(50))
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

class Planner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True))
    item = db.Column(db.String(200))
    dishfk = db.Column(db.Integer, db.ForeignKey(
        'dish.id', ondelete="CASCADE"), nullable=True)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 

#ToDo List
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(500))
    project = db.Column(db.String(50))
    checked = db.Column(db.BOOLEAN)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 
    
#Medical
class Facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    address=db.Column(db.String(100))
    city=db.Column(db.String(50))
    state=db.Column(db.String(2))
    zip=db.Column(db.String(10))
    phone=db.Column(db.String(20))
    type = db.Column(db.String(50))
    userid = db.Column(db.Integer, nullable=False)
    #relationship
    doctor = db.relationship('Doctor', backref='facility', passive_deletes=True)
    hosptial = db.relationship('Hosptial', backref='facility', passive_deletes=True)
    surgeries = db.relationship('Surgeries', backref='facility', passive_deletes=True)
    
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    address=db.Column(db.String(100))
    city=db.Column(db.String(50))
    state=db.Column(db.String(2))
    zip=db.Column(db.String(10))
    phone=db.Column(db.String(15))
    email=db.Column(db.String(100))
    asst=db.Column(db.String(100))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    #relationships
    hosptial = db.relationship('Hosptial', backref='doctor', passive_deletes=True)
    surgeries = db.relationship('Surgeries', backref='doctor', passive_deletes=True)
    medication = db.relationship('Medications', backref='doctor', passive_deletes=True)
    #forignkeys
    facilityfk=db.Column(db.Integer, db.ForeignKey(
        'facility.id', ondelete="CASCADE"), nullable=False)

class Hosptial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datestart=db.Column(db.Date, nullable=False)
    dateend=db.Column(db.Date, nullable=False)
    reason=db.Column(db.String(100))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 
    #forign keys
    doctorfk=db.Column(db.Integer, db.ForeignKey('doctor.id', ondelete="CASCADE"), nullable=False)
    facilityfk=db.Column(db.Integer, db.ForeignKey('facility.id', ondelete="CASCADE"), nullable=False)
    
class Surgeries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    date=db.Column(db.Date, nullable=False)
    description=db.Column(db.String(500))
    body_part=db.Column(db.String(50))
    age=db.Column(db.Integer)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 
    #forign keys
    doctorfk = db.Column(db.Integer, db.ForeignKey('doctor.id', ondelete="CASCADE"), nullable=False)
    facilityfk=db.Column(db.Integer, db.ForeignKey('facility.id', ondelete="CASCADE"), nullable=False)

class Medications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    dose=db.Column(db.String(50))
    how_often=db.Column(db.String(100))
    num_filled_days=db.Column(db.Integer)
    reason_for_taking=db.Column(db.String(100))
    pharmacy = db.Column(db.String(100))
    userid = db.Column(db.Integer, nullable=False)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 
    #forign keys
    doctorfk = db.Column(db.Integer, db.ForeignKey('doctor.id', ondelete="CASCADE"), nullable=False)

class Allergies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    reaction=db.Column(db.String(50))
    dateadded=db.Column(db.Date, nullable=False)
    userid = db.Column(db.Integer, nullable=False)
    update_time = db. Column (db. DateTime, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now()) 