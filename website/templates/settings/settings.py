from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
import flask_login
from sqlalchemy.sql import desc
from website.models import *
from website import db
import datetime, json

settings = Blueprint("settings", __name__)

@settings.route("/", methods=['GET','POST'])
@login_required
def settingsHome():
    # FIXME:figure out how to dynamically get info from form and save to db
    if request.method == 'POST':
        # cols = Settings.__table__.columns.keys()
        # us = db.session.query(Settings).filter(Settings.userid == flask_login.current_user.id).first()
        # for col in cols[2:-2]:
        #     us.getattr(Settings, col) = request.form.get(col)
        pass
        return redirect(url_for('settings.settingsHome'))
    
    cols = Settings.__table__.columns.keys()
    
    dic_cols = []
    for col_name in cols[2:-2]:
        key = col_name
        label = key
        dbvalue = db.session.query(getattr(Settings, key)).filter(Settings.userid == flask_login.current_user.id).first()
        if dbvalue[0] == None: value=False
        elif dbvalue[0] == True: value=True
        elif dbvalue[0] == False: value=False
        else: value = False
        dic_cols.append([value,label])
    
    us = db.session.query(Settings).filter(Settings.userid == flask_login.current_user.id).first()
    return render_template('settings/settings.html', user=User, us=us, values=dic_cols)