from operator import itemgetter
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.sql.expression import join
from .models import Dish, Planner, Steps, User, Recipe, Todo
from .notion import get_supplies, get_menu
from datetime import datetime, timedelta
import datetime
from . import db
from .makedates import makedates
from .nutrition import get_food_item, nutrition_single
import sys
from subprocess import run, PIPE
from sqlalchemy.sql import func


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("home.html", user=User)


@views.route("/cpap", methods=['GET','POST'])
@login_required
def cpap():
    if request.method == "POST":
        run([sys.executable,'cpap/main.py'], shell=False, stdout=PIPE)
        flash("Order Script ran!", category='sucess')
        return redirect(url_for('views.cpap'))
    
    supplies = get_supplies()
    cpapsupplies = []
    for i in range(len(supplies['results'])):
        id = supplies['results'][i]['id']
        item = supplies['results'][i]['properties']['Item']['title'][0]['plain_text']
        itemNum = supplies['results'][i]['properties']['Item#']['rich_text'][0]['plain_text']
        howOften = supplies['results'][i]['properties']['How often (days)']['number']
        lastOrdered = datetime.datetime.strptime(supplies['results'][i]['properties']['Last Ordered']['date']['start'],"%Y-%m-%d")
        imgUrl = supplies['results'][i]['properties']['ImageURL']['url']
        nextOrder = datetime.datetime.strptime(supplies['results'][i]['properties']['Last Ordered']['date']['start'],"%Y-%m-%d") + timedelta(days=howOften)
        littlesupply = [id,item,itemNum,howOften,lastOrdered.strftime("%m-%d-%Y"),imgUrl,nextOrder.strftime("%m-%d-%Y")]
        cpapsupplies.append(littlesupply)
    cpapsupplies.sort(key= lambda x: x[6])
    return render_template("cpap.html", user=User, supplies = cpapsupplies)

@views.route("/menu", methods=['GET', 'POST'])
@login_required
def menu():
    # makedates()
    if request.method == 'POST':
        plan = Planner(
            date = datetime.datetime.strptime(request.form.get('datefield'),"%Y-%m-%d %H:%M:%S.%f"),
            # date = request.form.get('datefield'),
            item = Dish.query.filter_by(id=request.form.get('dishid')).first().name,
            dishfk = request.form.get('dishid')
        )
        db.session.add(plan)
        db.session.commit()
        
    dishlist = Dish.query.order_by(Dish.name).all()
    plans = Planner.query.order_by(Planner.date).limit(90)
    items = Recipe.query.order_by(Recipe.dishfk).all()
    ref = db.session.query(Planner.id, Planner.date).group_by(Planner.date).order_by(Planner.date)
    
    return render_template("menu.html", user=User, dishes=dishlist, plans=plans, items=items, ref=ref)


@views.route("/plan/single", methods=['GET', 'POST'])
@login_required
def menu_single():
    if request.method == 'POST':
        date = request.form.get('dateselector')
        
        recipes = db.session.query(\
            Recipe.carb_fiber, Recipe.carb_total, Recipe.catagory, Recipe.dishfk, Recipe.ing, Recipe.qty, Recipe.measurement, Recipe.notes)\
                .join(Dish, Dish.id == Recipe.dishfk)\
                    .join(Planner, Planner.dishfk == Recipe.dishfk)\
                        .filter(func.date(Planner.date) == date)\
                            .order_by(Recipe.date_created)\
                                .all()
        
        dishes = db.session.query(\
            Dish.id, Dish.cookTemp, Dish.cookTime, Dish.numServings, Dish.prepTime, Dish.servingSize)\
                .join(Planner, Planner.dishfk == Dish.id)\
                    .filter(func.date(Planner.date) == date)\
                         .all()
                         
        steps = db.session.query(\
            Steps.step_num, Steps.step_text, Steps.dishfk)\
                .join(Dish, Dish.id == Steps.dishfk)\
                    .join(Planner, Planner.dishfk == Steps.dishfk)\
                        .filter(func.date(Planner.date) == date)\
                            .all()
                                
        items = db.session.query(\
            Planner.date, Planner.dishfk, Planner.id, Planner.dishfk, Planner.item, Dish.pictureURL)\
                .join(Dish, Dish.id == Planner.dishfk)\
                    .filter(func.date(Planner.date) == date)\
                        .all()
                        
        return render_template("plan_single.html", user=User, recipes=recipes, dishs=dishes, steps=steps, items=items)

# Recipe Functions
@views.route("/menu/recipe", methods=['GET', 'POST'])
@login_required
def recipe():
    dishes = Dish.query.order_by(Dish.name).all()
    recipes = Recipe.query.all()
    steps = Steps.query.all()
    return render_template("recipe.html", user=User, dishes=dishes, recipes=recipes, steps=steps)


@views.route("/menu/recipe/<id>", methods=['GET', 'POST'])
@login_required
def recipe_single(id):
    if request.method == "POST":
        step = request.form['submit_button']
        if request.form['submit_button'] == 'Steps':
            num = Steps.query.filter_by(dishfk=id).all()
            
            step = Steps(
                step_text = request.form.get('stepdesc'),
                step_num = len(num)+1,
                dishfk = id
            )
            db.session.add(step)
            db.session.commit()
        else:
           
            #info for nutrition
            if request.form.get("notes") == None:
                fullitem = request.form.get("qty")+" "+request.form.get("measurement").title()+" "+request.form.get("ing").title()
            else:
                fullitem = request.form.get("qty")+" "+request.form.get("measurement").title()+" "+request.form.get("ing").title()+", "+request.form.get("notes")
            
            #get nutrition informtion  
            nutrition = get_food_item(fullitem)
            
            #build insert commnd to place data into database
            item = Recipe(
                qty=request.form.get("qty"), 
                measurement= request.form.get("measurement").title(), 
                ing= request.form.get("ing").title(),
                notes=request.form.get("notes"), 
                dishfk=request.form.get("dishid"),
                catagory = request.form.get('catagory'),
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
            #add and commit the record to the database
            db.session.add(item)
            db.session.commit()
    
    dish = Dish.query.filter_by(id=id).first()
    ings = Recipe.query.filter_by(dishfk=id).all()
    steps = Steps.query.filter_by(dishfk=id).all()
    allnutrition = nutrition_single(ings)
    
    list_of_catagories = ['Beverages', 'Bread/Bakery', 'Canned/Jarred Goods', 'Dairy', 'Dry/Baking Goods', 'Frozen Foods', 'Meat', 'Produce', 'Cleaners', 'Paper Goods', 'Personal Care', 'Other']
    
    return render_template("recipe-single.html", user=User, dish=dish, recipes=ings, nutrition=allnutrition, steps=steps, catagories=list_of_catagories)

@views.route("/deletingIng/<recID>/<dishID>")
@login_required
def deleteIng(recID,dishID):
    Recipe.query.filter_by(id=recID).delete()
    db.session.commit()
    return recipe_single(dishID)

@views.route("/deletingStep/<stepID>/<dishID>")
@login_required
def deleteStep(stepID,dishID):
    Steps.query.filter_by(id=stepID).delete()
    db.session.commit()
    return redirect(url_for('views.recipe_single', id=dishID))

@views.route("/deletingPlan/<id>")
@login_required
def deletePlan(id):
    Planner.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('views.menu'))


@views.route("/menu/recipe/<id>/update", methods=['POST'])
@login_required
def recipe_update(id):
    if request.method == 'POST':
        update = Dish.query.filter_by(id=id).first()
        update.pictureURL = request.form.get("picurl")
        update.numServings = request.form.get("servings")
        update.servingSize = request.form.get("servingSize")
        update.prepTime = request.form.get("prepTime")
        update.cookTime = request.form.get("cooktime")
        update.cookTemp = request.form.get("cookTemp")  
        db.session.commit()
    return redirect(url_for('views.recipe_single', id=id))


@views.route("/menu/recipe/new", methods=['GET', 'POST'])
@login_required
def recipe_new():
    if request.method == 'POST':
        newdish = Dish(
            name = request.form.get('dishName'),
            pictureURL = request.form.get('picURL'),
            numServings = request.form.get('servings'),
            servingSize = request.form.get('servingSize'),
            cookTime = request.form.get('cooktime'),
            prepTime = request.form.get('prepTime'),
            cookTemp = request.form.get('cookTemp')
        )
        db.session.add(newdish)
        db.session.commit()
        
        id = Dish.query.filter_by(name=request.form.get('dishName')).first().id
        return redirect(url_for('views.recipe_single', id=id))
    
    return render_template("new.html", user=User)


# Todo list
@views.route("/todo", methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        task = Todo(
            item = request.form.get('item').title(),
            project = request.form.get("project").title(),
            checked = request.form.get("checked")
        )
        db.session.add(task)
        db.session.commit()

    items = Todo.query.order_by(Todo.project.asc(), Todo.item.asc()).limit(100).all()
    return render_template("todo.html", user=User, items=items)


@views.route("/deletingTodo/<id>")
@login_required
def deleteTodo(id):
    Todo.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('views.todo'))

#Shopping Functions
@views.route("/menu/shopping", methods=['GET', 'POST'])
@login_required
def shopping():
    # makedates()
    if request.method == 'POST':
        pass
        
    items = db.session.query(Recipe.ing, Recipe.catagory, Recipe.dishfk, func.count(Recipe.ing).label('IngCount')).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.ing).order_by(Recipe.ing).all()
    counts = db.session.query(Recipe.catagory, func.count(Recipe.catagory)).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.catagory).all()

    
    
    return render_template("shopping.html", user=User, items=items, counts=counts)#, dishes=dishlist, plans=plans)