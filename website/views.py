from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Dish, User, Recipe
from .notion import get_supplies, get_menu
from datetime import datetime
from datetime import timedelta
from . import db
from sqlalchemy import func
import inflect


views = Blueprint("views", __name__)

    
def printnumber(numberoftimes):
    n2w = inflect.engine()
    number = n2w.number_to_words(numberoftimes).title().replace("-","")
    return number
        
    
def get_dishes():
    dishes = Dish.query.all()
    count = 1
    dishlist = []
    for dish in dishes:
        id = printnumber(count)
        littlelist = [id, dish.name]
        dishlist.append(littlelist)
        count += 1
    dishlist.sort(key=lambda x: x[1])
    return dishlist


@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("home.html", user=User)

@views.route("/cpap")
@login_required
def cpap():
    supplies = get_supplies()
    cpapsupplies = []
    for i in range(len(supplies['results'])):
        id = supplies['results'][i]['id']
        item = supplies['results'][i]['properties']['Item']['title'][0]['plain_text']
        itemNum = supplies['results'][i]['properties']['Item#']['rich_text'][0]['plain_text']
        howOften = supplies['results'][i]['properties']['How often (days)']['number']
        lastOrdered = datetime.strptime(supplies['results'][i]['properties']['Last Ordered']['date']['start'],"%Y-%m-%d")
        imgUrl = supplies['results'][i]['properties']['ImageURL']['url']
        nextOrder = datetime.strptime(supplies['results'][i]['properties']['Last Ordered']['date']['start'],"%Y-%m-%d") + timedelta(days=howOften)
        littlesupply = [id,item,itemNum,howOften,lastOrdered.strftime("%m-%d-%Y"),imgUrl,nextOrder.strftime("%m-%d-%Y")]
        cpapsupplies.append(littlesupply)
    cpapsupplies.sort(key= lambda x: x[6])
    return render_template("cpap.html", user=User, supplies = cpapsupplies)

@views.route("/menu")
@login_required
def menu():
    
    return render_template("menu.html", user=User)

@views.route("/menu/recipe", methods=['GET', 'POST'])
@login_required
def recipe():
    if request.method == "POST":
        qty = request.form.get("qty")
        measurement = request.form.get("measurement")
        ing = request.form.get("ing")
        notes = request.form.get("notes")
        
        item = Recipe(qty=qty, measurement=measurement, ing=ing, notes=notes)
        db.session.add(item)
        db.session.commit()
        flash('Recipe created!', category='success')
    else:
        dishlist = get_dishes()
    return render_template("recipe.html", user=User, dishes=dishlist)

@views.route("/menu/dishes")
@login_required
def dishes():
    dishlist = get_dishes()
    return render_template("dishes.html", user=User, dishes=dishlist)