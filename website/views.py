from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, after_this_request
from flask_login import login_required, current_user
from sqlalchemy.orm import session
from website.models import *
from datetime import datetime, timedelta
from . import db
from website.makedates import makedates
from website.nutrition import get_food_item, nutrition_single
from sqlalchemy.sql import func
import datetime, sys, pdfkit, flask_login, os
from math import ceil
from website.wifiqrcode import generate_code

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    currentvalue = db.session.query(func.max(A1C.date).label('ld'), A1C.testresult, A1C.userid).filter(A1C.userid == flask_login.current_user.id).order_by(A1C.date).first()
    if currentvalue.testresult is None:
        eag=0
    else:
        eag = ceil(28.7 * currentvalue.testresult - 46.7)
    cntProjects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).filter(Projects.next_review <= datetime.datetime.now()).filter(Projects.status != "Complete").count()
    cntMeds = db.session.query(Medications).filter(Medications.next_refill <= datetime.datetime.now()+timedelta(days=5)).filter(Medications.userid == flask_login.current_user.id).count()
    cntTasks = db.session.query(Tasks.id, Tasks.duedate, Tasks.checked, Tasks.item, Tasks.project, Tasks.userid, Projects.name.label('nameOfProject')).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.duedate <= (datetime.datetime.today()+timedelta(days=2))).filter(Tasks.checked==False).order_by(Tasks.duedate.desc(), Tasks.project).count()
    projects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).filter(Projects.next_review <= datetime.datetime.now()).filter(Projects.status != "Complete").all()
    tasks = db.session.query(Tasks.id, Tasks.duedate, Tasks.checked, Tasks.item, Tasks.project, Tasks.userid, Projects.name.label('nameOfProject')).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.duedate <= (datetime.datetime.today()+timedelta(days=2))).filter(Tasks.checked==False).order_by(Tasks.duedate.desc(), Tasks.project).all()
    plans = db.session.query(Planner).filter(Planner.date >= (datetime.datetime.today()- timedelta(days=1))).order_by(Planner.date).limit(10)
    meds = db.session.query(Medications).filter(Medications.next_refill <= (datetime.datetime.today()+timedelta(days=5))).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.next_refill).all()
    
    #TODO: figure out why the menu does not update when new informaion is added to a plan when the plan is already showing up.
    return render_template("home.html", user=User, meds=meds, currentvalue=currentvalue, eag=eag, plans=plans, tasks=tasks, projects=projects, cntTasks=cntTasks, cntMeds=cntMeds, cntProjects=cntProjects)

@views.route("/menu", methods=['GET', 'POST'])
@login_required
def menu():
    #see if there are more than 60 dates from today and if not make them
    records = db.session.query(func.count(Planner.id).label('totalcount')).filter(Planner.date >= datetime.datetime.today()).all()
    maxdate = db.session.query(func.max(Planner.date).label('max_date')).first()
    if records[0][0] <= 60:
        makedates(datetime.datetime.strftime(maxdate.max_date,"%Y-%m-%d"))
    # makedates(howmany=1, startdate='2021-01-01')
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
    
    return render_template("menu.html", user=User, dishes=dishlist, plans=plans, items=items, ref=ref)


@views.route("/plan/single/<date>", methods=['GET', 'POST'])
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
            return redirect(url_for('views.menu_single',date=ref[-10:]))
                
        recipes = db.session.query(\
            Recipe.carb_fiber, Recipe.carb_total, Recipe.catagory, Recipe.dishfk, Recipe.ing, Recipe.qty, Recipe.measurement, Recipe.notes)\
                .join(Dish, Dish.id == Recipe.dishfk)\
                    .join(Planner, Planner.dishfk == Recipe.dishfk)\
                        .filter(func.date(Planner.date) == date)\
                            .order_by(Recipe.date_created)\
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
                        
        dishes = db.session.query(\
            Dish.id, Dish.cookTemp, Dish.cookTime, Dish.numServings, Dish.prepTime, Dish.servingSize)\
                .join(Planner, Planner.dishfk == Dish.id)\
                    .filter(func.date(Planner.date) == date)\
                            .all()
    #TODO: figure out why when you add an existing receipe to a plan, the page returns blank                  
        dishesForList = db.session.query(Dish).all()
        return render_template("plan_single.html", user=User, recipes=recipes, dishs=dishes, steps=steps, items=items, dishlist=dishesForList)

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
        
        id = Dish.query.filter_by(name=request.form.get('dishName')).first()
        return redirect(url_for('views.recipe_single', id=id))
    
    return render_template("new.html", user=User)


#Shopping Functions
@views.route("/menu/shopping", methods=['GET', 'POST'])
# @login_required
def shopping():
    if request.method == 'POST':
        if request.form['exportPDF'] == 'exportPDF':
            pdfkit.from_url("http://127.0.0.1:5000"+url_for('views.shopping'), 'shopping.pdf')
    items = db.session.query(Recipe.ing, Recipe.catagory, Recipe.dishfk, func.count(Recipe.ing).label('IngCount')).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.ing).order_by(Recipe.ing).all()
    counts = db.session.query(Recipe.catagory, func.count(Recipe.catagory)).filter(Recipe.dishfk == Planner.dishfk).group_by(Recipe.catagory).all()
    return render_template("shopping.html", user=User, items=items, counts=counts)#, dishes=dishlist, plans=plans)




# Productivity
@views.route("/productivity", methods=['GET', 'POST'])
@login_required
def productivity():
    return render_template("productivity/productivity.html", user=User)

@views.route("productivity/goals", methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        newGoal = Goals(
            name = request.form.get('name'),
            pictureurl = request.form.get('pictureurl'),
            status = request.form.get('status'),
            measurement = request.form.get('measurement'),
            datestart = datetime.datetime.strptime(request.form.get('datestart'), "%Y-%m-%d"),
            dateend = datetime.datetime.strptime(request.form.get('dateend'), "%Y-%m-%d"),
            userid = request.form.get('thisuserid'),
        )
        db.session.add(newGoal)
        db.session.commit()
    
    completedTasks = db.session.query(Tasks.goalfk,func.count(Tasks.id).label('count')).filter(Tasks.checked == True).group_by(Tasks.goalfk).all()
    allTasks = db.session.query(Tasks.goalfk,func.count(Tasks.id).label('count')).group_by(Tasks.goalfk).all()
    
    percentcomplete=[]
    projects = []
    for completed in completedTasks:
        projects.append(completed[0])
        
    for i in range(len(allTasks)):
        allvalue=allTasks[i][0]
        if allvalue in projects:
            for a in range(len(allTasks)):
                if allTasks[i][0] == completedTasks[a][0]:
                    perc = round(completedTasks[a][1]/allTasks[i][1]*100,2)
                    percentcomplete.append(tuple((allTasks[i][0],perc)))
                    break
                else:
                    next
    
    goals = db.session.query(Goals).order_by(Goals.name).all()
    return render_template("productivity/goals.html", user=User, goals=goals, percentcomplete=percentcomplete)

@views.route("productivity/goals/<id>", methods=['GET', 'POST'])
@login_required
def goal_single(id):
    if request.method == 'POST':
        if request.form.get('complete') == 'on': complete = True 
        else: complete = False
        newtask = Tasks(
            project = None,
            item = request.form.get('task').title(),
            checked = complete,
            userid = request.form.get('thisuserid'),
            duedate = datetime.datetime.strptime(request.form.get('dueDate'),"%Y-%m-%d"),
            goalfk = request.form.get('goalfk')
        )
        db.session.add(newtask)
        db.session.commit()
        return redirect(url_for('views.goal_single', id=id))
    
    completedTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).filter(Tasks.checked == True).count()
    allTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).count()
    
    if allTasks == 0:
        percentcomplete = 0
    else:
        percentcomplete = round((completedTasks/allTasks)*100,2)

    goals = db.session.query(Goals).filter(Goals.userid == flask_login.current_user.id).filter(Goals.id == id).all()
    tasks = db.session.query(Tasks).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).order_by(Tasks.checked, Tasks.duedate, Tasks.item).all()
    return render_template("productivity/goals_single.html", user=User, goals=goals, tasks=tasks, percentcomplete=percentcomplete)

@views.route("productivity/noTOyes/<taskid>/<goalid>")
@login_required
def goalnoTOyes(taskid, goalid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('views.goal_single', id=goalid))

@views.route("productivity/yesTOno/<taskid>/<goalid>")
@login_required
def goalyesTOno(taskid, goalid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('views.goal_single', id=goalid))

@views.route("productivity/deletetask/<taskid>/<goalid>")
@login_required
def deletegoal(taskid, goalid):
    
    Tasks.query.filter_by(id=taskid).delete()
    db.session.commit()
    return redirect(url_for('views.goal_single', id=goalid))


@views.route("productivity/projects", methods=['GET', 'POST'])
@login_required
def projects():
    if request.method == 'POST':
        when = int(request.form.get('when_review'))
        nextrev = datetime.datetime.strptime(request.form.get('last_reviewed'),"%Y-%m-%d") + timedelta(days=when)
        newProj = Projects(
            name = request.form.get('name'),
            pictureurl = request.form.get('pictureurl'),
            status = request.form.get('status'),
            last_reviewed = datetime.datetime.strptime(request.form.get('last_reviewed'),"%Y-%m-%d"),
            when_review = request.form.get('when_review'),
            next_review = nextrev,
            userid = request.form.get('thisuserid')
        )
        db.session.add(newProj)
        db.session.commit()
    
    pros = db.session.query(Projects).all()
    for pro in pros:
        pro.next_review = pro.last_reviewed + timedelta(days=pro.when_review)
        db.session.commit()
    
    completedTasks = db.session.query(Tasks.project,func.count(Tasks.id).label('count')).filter(Tasks.checked == True).group_by(Tasks.project).all()
    allTasks = db.session.query(Tasks.project,func.count(Tasks.id).label('count')).group_by(Tasks.project).all()
    
    percentcomplete=[]
    projects = []
    for completed in completedTasks:
        projects.append(completed[0])
        
    for i in range(len(allTasks)):
        allvalue=allTasks[i][0]
        if allvalue in projects:
            for a in range(len(allTasks)):
                if allTasks[i][0] == completedTasks[a][0]:
                    perc = round(completedTasks[a][1]/allTasks[i][1]*100,2)
                    percentcomplete.append(tuple((allTasks[i][0],perc)))
                    break
                else:
                    next
    #TODO: make a way for user to update the reviewed date so it can re-calculate the next review date
    projects = db.session.query(Projects).order_by(Projects.name).all()
    return render_template("productivity/projects.html", user=User, projects=projects, percentcomplete=percentcomplete)

@views.route("productivity/tasks", methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        if request.form.get('complete') == 'on': complete = True 
        else: complete = False
        
        if request.form.get('project')[0] == "P":
            project = request.form.get('project')[1:]
            goalfk = None
        else:
            project = None
            goalfk = request.form.get('project')[1:]
        
        newtask = Tasks(
            project = project,
            item = request.form.get('task').title(),
            checked = complete,
            userid = request.form.get('thisuserid'),
            duedate = datetime.datetime.strptime(request.form.get('dueDate'),"%Y-%m-%d"),
            goalfk = goalfk
        )
        db.session.add(newtask)
        db.session.commit()
        
    projects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).order_by(Projects.name).all()
    goals = db.session.query(Goals).filter(Goals.userid == flask_login.current_user.id).order_by(Goals.name).all()
    complete = db.session.query(Projects.name.label('projectname'), Projects.status.label('projectstatus'), Tasks.checked, Tasks.duedate, Tasks.goalfk, Tasks.id, Tasks.item).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.checked == 0).order_by(Tasks.duedate, Tasks.project, Tasks.item).all()
    incomplete = db.session.query(Projects.name.label('projectname'), Projects.status.label('projectstatus'), Tasks.checked, Tasks.duedate, Tasks.goalfk, Tasks.id, Tasks.item).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.checked == 1).order_by(Tasks.project, Tasks.duedate, Tasks.item).all()
    return render_template("productivity/tasks.html", user=User, projects=projects, complete=complete, incomplete=incomplete, goals=goals)

@views.route("productivity/projects/<id>", methods=['GET', 'POST'])
@login_required
def project_single(id):
    if request.method == 'POST':
        if request.form['reviewupdate'] == 'Review Complete':
            udproject = db.session.query(Projects).filter(Projects.id == id).first()
            udproject.next_review = datetime.datetime.strptime(request.form.get('date_update'),"%Y-%m-%d") + timedelta(days=int(udproject.when_review))
            udproject.last_reviewed = datetime.datetime.strptime(request.form.get('date_update'),"%Y-%m-%d")
            db.session.commit()
            return redirect(url_for('views.home'))
        else:
            if request.form.get('complete') == 'on': complete = True 
            else: complete = False
            newtask = Tasks(
                project = request.form.get('project'),
                item = request.form.get('task').title(),
                checked = complete,
                userid = request.form.get('thisuserid'),
                duedate = datetime.datetime.strptime(request.form.get('dueDate'),"%Y-%m-%d"),
                goalfk = None
            )
            db.session.add(newtask)
            db.session.commit()
        return redirect(url_for('views.project_single', id=id))
    
    completedTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).filter(Tasks.checked == True).count()
    allTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).count()
    
    if allTasks == 0:
        percentcomplete = 0
    else:
        percentcomplete = round((completedTasks/allTasks)*100,2)

    projects = db.session.query(Projects.id, Projects.name, Projects.status, Projects.last_reviewed, Projects.when_review, Projects.pictureurl, Projects.userid).filter(Projects.userid == flask_login.current_user.id).filter(Projects.id == id).all()
    tasks = db.session.query(Tasks).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).order_by(Tasks.checked, Tasks.duedate, Tasks.item).all()
    return render_template("productivity/projects_single.html", user=User, projects=projects, tasks=tasks, percentcomplete=percentcomplete, today=datetime.datetime.today())

@views.route("productivity/noTOyes/<taskid>/<projectid>")
@login_required
def noTOyes(taskid, projectid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('views.project_single', id=projectid))

@views.route("productivity/yesTOno/<taskid>/<projectid>")
@login_required
def yesTOno(taskid, projectid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('views.project_single', id=projectid))

@views.route("productivity/deletetask/<taskid>/<projectid>")
@login_required
def deletetask(taskid, projectid):
    refeerer = request.referrer
    db.session.query(Tasks).filter(Tasks.id == taskid).delete()
    db.session.commit()
    return redirect(refeerer)

@views.route("productivity/importNotion")
@login_required
def importNotion():
    from .taskinport import get_tasks, getNextTasks, parsejsonMakeTask, notionidupdate
    
    notionidupdate()
    
    json = get_tasks()
    parsejsonMakeTask(json)
    
    while json['next_cursor'] != None:
        nextcursor = json['next_cursor']
        json = getNextTasks(nextcursor)
        parsejsonMakeTask(json)
    
    return redirect(url_for('views.tasks'))

@views.route("productivity/taskdelete/<taskid>")
@login_required
def taskdelete(taskid):
    refeerer = request.referrer
    db.session.query(Tasks).filter(Tasks.id == taskid).delete()
    db.session.commit()
    return redirect(refeerer)

@views.route("productivity/task_noTOyes/<taskid>")
@login_required
def task_noTOyes(taskid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('views.tasks'))

@views.route("productivity/task_yesTOno/<taskid>")
@login_required
def task_yesTOno(taskid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('views.tasks'))

@views.route("productivity/taskupdate/<taskid>", methods=['GET','POST'])
@login_required
def taskupdate(taskid):
    if request.method == 'POST':
        updatetask = Tasks.query.filter(Tasks.id == taskid).first()
        updatetask.item = request.form.get('name').title()
        updatetask.duedate = datetime.datetime.strptime(request.form.get('duedate'),"%Y-%m-%d")
        updatetask.userid = request.form.get('thisuserid')
        db.session.commit()
        return redirect(url_for('views.tasks'))

    task = db.session.query(Projects.name.label('projectname'), Projects.status.label('projectstatus'), Tasks.checked, Tasks.duedate, Tasks.goalfk, Tasks.id, Tasks.item).join(Projects, Projects.id == Tasks.project).filter(Tasks.id == taskid).all()
    return render_template("productivity/taskupdate.html", user=User, task=task)

#FIXME: fix next review issue
# @views.route('/updatewhen')
# def updatewhen():
#     updatetask = db.session.query(Projects.last_reviewed, Projects.when_review, Projects.next_review).all()
#     for ut in updatetask:
#         newtime = ut.last_reviewed + timedelta(days=ut.when_review)
#         ut[2] = newtime
#         db.session.commit()
#         return render_template(url_for(views.projects))

@views.route("/health/a1c/delete/<id>")
@login_required
def deleteA1C(id):
    A1C.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('views.a1c'))

@views.route("/health/surgery/delete/<id>")
@login_required
def deleteSurg(id):
    Surgeries.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('views.surgeries'))

@views.route("/wifidelete/<id>")
@login_required
def wifidelete(id):
    file = db.session.query(Wifi.path).filter_by(id=id).first()
    if os.path.exists('website/'+file.path):
        Wifi.query.filter_by(id=id).delete()
        db.session.commit()
        os.remove('website/'+file.path)
    else:
        print("The file does not exist")

    return redirect(url_for('views.wifi'))

@views.route("/wifi", methods=['GET','POST'])
@login_required
def wifi():
    if request.method == 'POST':
        path = generate_code(request.form.get('ssid'), request.form.get('password'))
        newwifi = Wifi(
            SSID = request.form.get('ssid'),
            password = request.form.get('password'),
            path = path,
            userid = request.form.get('thisuserid')
        )
        db.session.add(newwifi)
        db.session.commit()
    # TODO: Figure out why this does not work on the website version of the program
    wifi = db.session.query(Wifi).filter(Wifi.userid == flask_login.current_user.id).order_by(Wifi.update_time).all()
    return render_template('wifi.html', user=User, wifi=wifi)

@views.route("/profile", methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        profile = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
        profile.firstname = request.form.get('firstname')
        profile.lastname = request.form.get('lastname')
        profile.address = request.form.get('address')
        profile.city = request.form.get('city')
        profile.state = request.form.get('state')
        profile.zip = request.form.get('zip')
        profile.phone = request.form.get('phone')
        profile.email = request.form.get('email')
        profile.username = request.form.get('un')
        profile.password = request.form.get('pw')
        profile.avatar = request.form.get('avatar')
        db.session.commit()
        return redirect(url_for("views.profile"))
        
    states = db.session.query(States).all()
    profile = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
    return render_template('profile.html', user=User, profile=profile, states=states)