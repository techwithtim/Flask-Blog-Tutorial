from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, after_this_request
from flask_login import login_required, current_user
from sqlalchemy.orm import session
from website.models import *
from datetime import datetime, timedelta
from website import db

from website.makedates import makedates
from website.nutrition import get_food_item, nutrition_single
from sqlalchemy.sql import func
import datetime, sys, pdfkit, flask_login, os
from math import ceil
from website.wifiqrcode import generate_code

prod = Blueprint("prod", __name__)

# Productivity
@prod.route("/", methods=['GET', 'POST'])
@login_required
def productivity():
    return render_template("productivity/productivity.html", user=User)

@prod.route("/goals", methods=['GET', 'POST'])
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

@prod.route("/goals/<id>", methods=['GET', 'POST'])
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
        return redirect(url_for('health.goal_single', id=id))
    
    completedTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).filter(Tasks.checked == True).count()
    allTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).count()
    
    if allTasks == 0:
        percentcomplete = 0
    else:
        percentcomplete = round((completedTasks/allTasks)*100,2)

    goals = db.session.query(Goals).filter(Goals.userid == flask_login.current_user.id).filter(Goals.id == id).all()
    tasks = db.session.query(Tasks).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.goalfk == id).order_by(Tasks.checked, Tasks.duedate, Tasks.item).all()
    return render_template("/goals_single.html", user=User, goals=goals, tasks=tasks, percentcomplete=percentcomplete)

@prod.route("/noTOyes/<taskid>/<goalid>")
@login_required
def goalnoTOyes(taskid, goalid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('health.goal_single', id=goalid))

@prod.route("/yesTOno/<taskid>/<goalid>")
@login_required
def goalyesTOno(taskid, goalid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('health.goal_single', id=goalid))

@prod.route("/deletetask/<taskid>/<goalid>")
@login_required
def deletegoal(taskid, goalid):
    
    Tasks.query.filter_by(id=taskid).delete()
    db.session.commit()
    return redirect(url_for('health.goal_single', id=goalid))


@prod.route("/projects", methods=['GET', 'POST'])
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

@prod.route("/tasks", methods=['GET', 'POST'])
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
    return render_template("/productivity/tasks.html", user=User, projects=projects, complete=complete, incomplete=incomplete, goals=goals)

@prod.route("/projects/<id>", methods=['GET', 'POST'])
@login_required
def project_single(id):
    if request.method == 'POST':
        if request.form['reviewupdate'] == 'Review Complete':
            udproject = db.session.query(Projects).filter(Projects.id == id).first()
            udproject.next_review = datetime.datetime.strptime(request.form.get('date_update'),"%Y-%m-%d") + timedelta(days=int(udproject.when_review))
            udproject.last_reviewed = datetime.datetime.strptime(request.form.get('date_update'),"%Y-%m-%d")
            db.session.commit()
            return redirect(url_for('health.home'))
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
        return redirect(url_for('health.project_single', id=id))
    
    completedTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).filter(Tasks.checked == True).count()
    allTasks = db.session.query(Tasks.item).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).count()
    
    if allTasks == 0:
        percentcomplete = 0
    else:
        percentcomplete = round((completedTasks/allTasks)*100,2)

    projects = db.session.query(Projects.id, Projects.name, Projects.status, Projects.last_reviewed, Projects.when_review, Projects.pictureurl, Projects.userid).filter(Projects.userid == flask_login.current_user.id).filter(Projects.id == id).all()
    tasks = db.session.query(Tasks).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.project == id).order_by(Tasks.checked, Tasks.duedate, Tasks.item).all()
    return render_template("/projects_single.html", user=User, projects=projects, tasks=tasks, percentcomplete=percentcomplete, today=datetime.datetime.today())

@prod.route("/noTOyes/<taskid>/<projectid>")
@login_required
def noTOyes(taskid, projectid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('health.project_single', id=projectid))

@prod.route("/yesTOno/<taskid>/<projectid>")
@login_required
def yesTOno(taskid, projectid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('health.project_single', id=projectid))

@prod.route("/deletetask/<taskid>/<projectid>")
@login_required
def deletetask(taskid, projectid):
    refeerer = request.referrer
    db.session.query(Tasks).filter(Tasks.id == taskid).delete()
    db.session.commit()
    return redirect(refeerer)

@prod.route("/importNotion")
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
    
    return redirect(url_for('prod.tasks'))

@prod.route("/taskdelete/<taskid>")
@login_required
def taskdelete(taskid):
    refeerer = request.referrer
    db.session.query(Tasks).filter(Tasks.id == taskid).delete()
    db.session.commit()
    return redirect(refeerer)

@prod.route("/task_noTOyes/<taskid>")
@login_required
def task_noTOyes(taskid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = True
    db.session.commit()
    return redirect(url_for('prod.tasks'))

@prod.route("/task_yesTOno/<taskid>")
@login_required
def task_yesTOno(taskid):
    
    task = Tasks.query.filter_by(id=taskid).first()
    task.checked = False
    db.session.commit()
    return redirect(url_for('prod.tasks'))

@prod.route("/taskupdate/<taskid>", methods=['GET','POST'])
@login_required
def taskupdate(taskid):
    if request.method == 'POST':
        updatetask = Tasks.query.filter(Tasks.id == taskid).first()
        updatetask.item = request.form.get('name').title()
        updatetask.duedate = datetime.datetime.strptime(request.form.get('duedate'),"%Y-%m-%d")
        updatetask.userid = request.form.get('thisuserid')
        db.session.commit()
        return redirect(url_for('prod.tasks'))

    task = db.session.query(Projects.name.label('projectname'), Projects.status.label('projectstatus'), Tasks.checked, Tasks.duedate, Tasks.goalfk, Tasks.id, Tasks.item).join(Projects, Projects.id == Tasks.project).filter(Tasks.id == taskid).all()
    return render_template("productivity/taskupdate.html", user=User, task=task)