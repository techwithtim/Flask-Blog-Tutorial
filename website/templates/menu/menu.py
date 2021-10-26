from flask import Blueprint, render_template, request, redirect, url_for
from flask.helpers import flash
from flask_login import login_required
from website.models import *
from datetime import datetime, timedelta
from website import db
from website.makedates import makedates
from website.nutrition import get_food_item, nutrition_single
from sqlalchemy.sql import func
import datetime, pdfkit
from website.scrape_recipe import *


menu = Blueprint("menu", __name__)


@menu.route("/", methods=['GET', 'POST'])
@login_required
def menuHome():
    records = db.session.query(func.count(Planner.id).label('totalcount')).filter(Planner.date >= datetime.datetime.today()).all()
    maxdate = db.session.query(func.max(Planner.date).label('max_date')).first()
    if records[0][0] <= 60:
        makedates(datetime.datetime.strftime(maxdate.max_date,"%Y-%m-%d"))
    if request.method == 'POST':
        plan = Planner(
            date = datetime.datetime.strptime(request.form.get('datefield'),"%Y-%m-%d %H:%M:%S"),
            # date = request.form.get('datefield'),
            item = Dish.query.filter_by(id=request.form.get('dishid')).first().name,
            dishfk = request.form.get('dishid')
        )
        db.session.add(plan)
        db.session.commit()
        
    dishlist = Dish.query.order_by(Dish.name).all()
    plans = Planner.query.filter(Planner.date >= (datetime.datetime.today()- timedelta(days=2))).order_by(Planner.date).limit(60)
    items = Recipe.query.order_by(Recipe.dishfk).all()
    ref = db.session.query(Planner.id, Planner.date).group_by(Planner.date).order_by(Planner.date)
    
    return render_template("menu/menu.html", user=User, dishes=dishlist, plans=plans, items=items, ref=ref)


@menu.route("/<date>", methods=['GET', 'POST'])
@login_required
def menu_single(date):
    # FIXME: why it does not return when saving
    if request.method == 'POST':
        if request.form.get('AddDishToPlanner') == "AddDishToPlanner":
            ref = request.referrer
            plan = Planner(
                date = datetime.datetime.strptime(request.form.get('datefield'),"%Y-%m-%d %H:%M:%S"),
                # date = request.form.get('datefield'),
                item = Dish.query.filter_by(id=request.form.get('dishid')).first().name,
                dishfk = request.form.get('dishid')
            )
            db.session.add(plan)
            db.session.commit() 
            ## FIXME: when entering a date manually, it does not return anything
            return redirect(url_for('menu.plan_single',date=ref[-10:]))
                
        recipes = db.session.query(\
            Recipe.carb_fiber, Recipe.carb_total, Recipe.catagory, Recipe.dishfk, Recipe.ing, Recipe.qty, Recipe.measurement, Recipe.notes)\
                .join(Dish, Dish.id == Recipe.dishfk)\
                    .join(Planner, Planner.dishfk == Recipe.dishfk)\
                        .filter(func.date(Planner.date) == func.date(date))\
                            .order_by(Recipe.date_created)\
                                .all()
        
                         
        steps = db.session.query(\
            Steps.step_num, Steps.step_text, Steps.dishfk)\
                .join(Dish, Dish.id == Steps.dishfk)\
                    .join(Planner, Planner.dishfk == Steps.dishfk)\
                        .filter(func.date(Planner.date) == func.date(date))\
                            .all()
                                
        items = db.session.query(\
            Planner.date, Planner.dishfk, Planner.id, Planner.dishfk, Planner.item, Dish.pictureURL)\
                .join(Dish, Dish.id == Planner.dishfk)\
                    .filter(func.date(Planner.date) == func.date(date))\
                        .all()
                        
        dishes = db.session.query(\
            Dish.id, Dish.cookTemp, Dish.cookTime, Dish.numServings, Dish.prepTime, Dish.servingSize)\
                .join(Planner, Planner.dishfk == Dish.id)\
                    .filter(func.date(Planner.date) == func.date(date))\
                            .all()
    #TODO: figure out why when you add an existing receipe to a plan, the page returns blank                  
        dishesForList = db.session.query(Dish).all()
        return render_template("menu/plan_single.html", user=User, recipes=recipes, dishs=dishes, steps=steps, items=items, dishlist=dishesForList)

# Recipe Functions
@menu.route("/recipe", methods=['GET', 'POST'])
@login_required
def recipe():
    dishes = Dish.query.order_by(Dish.name).all()
    recipes = Recipe.query.all()
    steps = Steps.query.all()
    return render_template("menu/recipe.html", user=User, dishes=dishes, recipes=recipes, steps=steps)


@menu.route("/recipe/<id>", methods=['GET', 'POST'])
@login_required
def recipe_single(id):
    if request.method == "POST":
        if request.form.get('submit_button') == 'Steps':
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
    
    return render_template("menu/recipe-single.html", user=User, dish=dish, recipes=ings, nutrition=allnutrition, steps=steps, catagories=list_of_catagories)

@menu.route("/deletingIng/<recID>/<dishID>")
@login_required
def deleteIng(recID,dishID):
    Recipe.query.filter_by(id=recID).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_single', id=dishID))

@menu.route("/deletingStep/<stepID>/<dishID>")
@login_required
def deleteStep(stepID,dishID):
    Steps.query.filter_by(id=stepID).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe_single', id=dishID))

@menu.route("/deletingPlan/<id>")
@login_required
def deletePlan(id):
    Planner.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('menu.menuHome'))


@menu.route("/recipe/delete/<id>", methods=['GET','POST'])
@login_required
def recipe_delete(id):
    db.session.query(Dish).filter(Dish.id == id).delete()
    db.session.commit()
    return redirect(url_for('menu.recipe'))

@menu.route("/recipe/<id>/update", methods=['POST'])
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
    return redirect(url_for('menu.recipe_single', id=id))


@menu.route("/recipe/new", methods=['GET', 'POST'])
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
        
        id = Dish.query.filter_by(name=request.form.get('dishName')).first()
        return redirect(url_for('menu.recipe_single', id=id))
    
    return render_template("menu/new.html", user=User)


@menu.route("/shopping", methods=['GET', 'POST'])
# @login_required
def shopping():
    if request.method == 'POST':
        if request.form['exportPDF'] == 'exportPDF':
            pdfkit.from_url("http://127.0.0.1:5000"+url_for('views.shopping'), 'shopping.pdf')
    items = db.session.query(Recipe.ing, Recipe.catagory, Recipe.dishfk, func.count(Recipe.ing).label('IngCount')).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.ing).order_by(Recipe.ing).all()
    counts = db.session.query(Recipe.catagory, func.count(Recipe.catagory)).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.catagory).all()
    return render_template("menu/shopping.html", user=User, items=items, counts=counts)#, dishes=dishlist, plans=plans)

@menu.route("/scrape", methods=['GET','POST'])
@login_required
def scrape():
    if request.method == "POST":
        webstite = request.form.get('website')
        scraper = scrape_recipe(webstite)
        dishid = make_dish(scraper[0][0],scraper[0][1],scraper[0][2])

        for ing in scraper[1][0]:
            nuts = get_food_item(ing)
            if nuts == 0:
                db.session.query(Dish).filter(Dish.id == dishid).delete()
                db.session.commit()
                flash("Problem importing.  Try again",category='error')
                return redirect(url_for('menu.menuHome'))
            make_recipe(nuts,dishid)

        i=1
        for step in scraper[2][0]:
            make_steps(step, dishid, i) 
            i += 1
        return redirect(url_for('menu.menuHome'))
    
    return render_template('menu/scrape.html', user=User)