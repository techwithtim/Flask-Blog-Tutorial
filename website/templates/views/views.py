from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from website.models import *
from datetime import datetime, timedelta
from website import db
from sqlalchemy.sql import func
import datetime, flask_login
from math import ceil
import os

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
    cntA1C = db.session.query(A1C).filter(A1C.userid == flask_login.current_user.id).count()
    projects = db.session.query(Projects).filter(Projects.userid == flask_login.current_user.id).filter(Projects.next_review <= datetime.datetime.now()).filter(Projects.status != "Complete").all()
    tasks = db.session.query(Tasks.id, Tasks.duedate, Tasks.checked, Tasks.item, Tasks.project, Tasks.userid, Projects.name.label('nameOfProject')).join(Projects, Projects.id == Tasks.project).filter(Tasks.userid == flask_login.current_user.id).filter(Tasks.duedate <= (datetime.datetime.today()+timedelta(days=2))).filter(Tasks.checked==False).order_by(Tasks.duedate.desc(), Tasks.project).all()
    plans = db.session.query(Planner).filter(Planner.date >= (datetime.datetime.today()- timedelta(days=1))).order_by(Planner.date).limit(10)
    meds = db.session.query(Medications).filter(Medications.next_refill <= (datetime.datetime.today()+timedelta(days=5))).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.next_refill).all()
    
    return render_template("views/home.html", user=User, meds=meds, currentvalue=currentvalue, eag=eag, plans=plans, tasks=tasks, projects=projects, cntTasks=cntTasks, cntMeds=cntMeds, cntProjects=cntProjects, cntA1C=cntA1C)


@views.route("/profile", methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        pic = request.files['avatar']
        mime = pic.mimetype
        filename = secure_filename(pic.filename)
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
        profile.avatar = pic.read()
        profile.avatar_filename = filename
        profile.avatar_mimetype = mime
        db.session.commit()
        
        filename = str(flask_login.current_user.id)+"."+mime[-3:]
        profile.avatar_filename = filename
        db.session.commit()
        
        pic.seek(0) 
        pic.save(os.path.join(url_for('static'),'images', filename))
        return redirect(url_for("views.profile"))
        
    states = db.session.query(States).all()
    profile = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
    return render_template('views/profile.html', user=User, profile=profile, states=states)