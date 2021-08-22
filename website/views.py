from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Dish, User, Recipe
from .notion import get_supplies, get_menu
from datetime import datetime
from datetime import timedelta
from . import db
from sqlalchemy import func

views = Blueprint("views", __name__)


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
    menu = Dish.query.all()
    maxdate = datetime.today().date()

    menulist = []
    for menu in menu:
        menulist.append(menu.item)
        date = menu.date_created.date()
        if date > maxdate:
            maxdate = date
    if maxdate + timedelta(days=1) < datetime.now().date():
        get_menu()
        menu = Dish.query.all()
    menulist.sort()
    return render_template("menu.html", user=User, menu=menulist)

@views.route("/menu/recipe")
@login_required
def ingredients():
    return render_template("recipe.html", user=User)

@views.route("/menu/dishes")
@login_required
def dishes():
    return render_template("dishes.html", user=User)