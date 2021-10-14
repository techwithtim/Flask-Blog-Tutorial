from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from website.models import *
from website import db

import flask_login, os
from website.wifiqrcode import generate_code

personal = Blueprint("personal", __name__)


@personal.route("/wifidelete/<id>")
@login_required
def wifidelete(id):
    file = db.session.query(Wifi).filter_by(id=id).first()
    if os.path.exists('website/static/'+file.path):
        os.remove('website/static/'+file.path)
        Wifi.query.filter_by(id=id).delete()
        db.session.commit()
    else:
        print("The file does not exist")

    return redirect(url_for('personal.wifi'))

@personal.route("/wifi", methods=['GET','POST'])
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
    return render_template('/personal/wifi.html', user=User, wifi=wifi)
