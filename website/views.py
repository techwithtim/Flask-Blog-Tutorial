from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Dish, Steps, User, Recipe
from .notion import get_supplies, get_menu
from datetime import datetime
from datetime import timedelta
from . import db
from sqlalchemy import func
import inflect, json
from .nutrition import get_food_item, nutrition_single


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
        littlelist = [id, dish.name, dish.id]
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
    dishes = Dish.query.all()
    recipes = Recipe.query.all()
    steps = Steps.query.all()
    return render_template("recipe.html", user=User, dishes=dishes, recipes=recipes, steps=steps)

@views.route("/menu/recipe/<id>", methods=['GET', 'POST'])
@login_required
def recipe_single(id):
    if request.method == "POST":
        if request.form.get('step_modal') == '':
            num = Steps.query.filter_by(dishfk=id).all()
            
            step = Steps(
                step_text = request.form.get('stepdesc'),
                step_num = len(num)+1,
                dishfk = id
            )
            db.session.add(step)
            db.session.commit()
            flash("Step Added", category='sucess')
        else:
            # Info from form
            qty = request.form.get("qty")
            measurement = request.form.get("measurement")
            ing = request.form.get("ing")
            notes = request.form.get("notes")
            dishid = request.form.get("dishid")

            #info from nutrition
            if notes == None:
                fullitem = qty+" "+measurement+" "+ing
            else:
                fullitem = qty+" "+measurement+" "+ing+", "+notes
                
            nutrition = get_food_item(fullitem)
            item = Recipe(
                qty=qty, 
                measurement=measurement, 
                ing=ing, 
                notes=notes, 
                dishfk=dishid,
                weight = nutrition['weight'],
                fat_total = nutrition['totalFat'],
                fat_sat = nutrition['satFat'],
                fat_trans = nutrition['transFat'],
                cholesterol = nutrition['cholesterol'],
                sodium = nutrition['sodium'],
                potassium = nutrition['potassium'],
                carb_total = nutrition['totalCarb'],
                carb_fiber = nutrition['fiber'],
                carb_sugar = nutrition['sugar'],
                protein = nutrition['protein'],
                servsize = nutrition['weight'],
                calories = nutrition['calories'],
                calories_fat = nutrition['totalFat']*9,
                pictureURL = nutrition['picURL'])
            
            db.session.add(item)
            db.session.commit()
            flash('Recipe created!', category='success')
    
    dish = Dish.query.filter_by(id=id).first()
    ings = Recipe.query.filter_by(dishfk=id).all()
    steps = Steps.query.filter_by(dishfk=id).all()
    allnutrition = nutrition_single(ings)
    
    return render_template("recipe-single.html", user=User, dish=dish, recipes=ings, nutrition=allnutrition, steps=steps)

@views.route("/menu/dishes")
@login_required
def dishes():
    dishlist = get_dishes()
    return render_template("dishes.html", user=User, dishes=dishlist)

@views.route("/deletingIng/<recID>/<dishID>")
@login_required
def deleteIng(recID,dishID):
    Recipe.query.filter_by(id=recID).delete()
    db.session.commit()
    return recipe_single(dishID)

@views.route("/deletingStep/<recID>/<dishID>")
@login_required
def deleteStep(stepID,dishID):
    Steps.query.filter_by(id=stepID).delete()
    db.session.commit()
    return redirect(url_for('views.recipe_single', id=dishID))

@views.route("/menu/recipe/<id>/update", methods=['POST'])
@login_required
def update(id):
    if request.method == 'POST':
        update = Dish.query.filter_by(id=id).first()
        update.pictureURL = request.form.get("picurl")
        db.session.commit()
    return redirect(url_for('views.recipe_single', id=id))
