from flask import Blueprint, render_template, request, redirect, url_for, send_file, after_this_request
from flask_login import login_required
from website.models import *
from website import db
from sqlalchemy.sql import desc
from dateutil import relativedelta



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

@personal.route("/code", methods=['GET','POST'])
@login_required
def code():
    return render_template("personal/codesnip.html", user=User)

@personal.route("/housinghistory", methods=['GET','POST'])
@login_required
def housinghistory():
    if request.method == "POST":
        newhh = HousingHistory(
            address = request.form.get('address'),
            city = request.form.get('city'),
            state = request.form.get('state'),
            zip = request.form.get('zip'),
            movein = datetime.datetime.strptime(request.form.get('start'),"%Y-%m"),
            moveout = datetime.datetime.strptime(request.form.get('end'),"%Y-%m"),
            userid = request.form.get('thisuserid')
        )
        db.session.add(newhh)
        db.session.commit()
    
    lived = db.session.query(HousingHistory).filter(HousingHistory.userid == flask_login.current_user.id).order_by(desc(HousingHistory.movein)).all()
    LOS = []
    for stay in lived:
        delta = relativedelta.relativedelta(stay.moveout, stay.movein)
        if delta.years >= 1:
            length = f'{delta.years} years, {delta.months} months'
        elif delta.years == 0 and delta.months == 1:
            length = f'{delta.months} month'
        elif delta.years == 0 and delta.months > 1:
            length = f'{delta.months} months'
        else: length = 'error'
        little = {}
        little['id'] = stay.id
        little['stay'] = length
        LOS.append(little)    
    
    states = db.session.query(States).all()
    housing = db.session.query(HousingHistory).filter(HousingHistory.userid == flask_login.current_user.id).order_by(desc(HousingHistory.movein)).all()
    return render_template("personal/housinghistory.html", user=User, housing=housing, states=states, los=LOS)

@personal.route("/housinghistory/<id>", methods=['GET','POST'])
@login_required
def edithousing(id):
    if request.method == "POST":
        house = db.session.query(HousingHistory).filter_by(id=id).first()
        house.movein = datetime.datetime.strptime(request.form.get('start'),"%Y-%m")
        house.moveout = datetime.datetime.strptime(request.form.get('end'),"%Y-%m")
        house.address = request.form.get('address')
        house.city = request.form.get('city')
        house.state = request.form.get('state')
        house.zip = request.form.get('zip')
        db.session.commit()
        return redirect(url_for('personal.housinghistory'))
    
    states = db.session.query(States).all()
    house = db.session.query(HousingHistory).filter_by(id=id).first()
    return render_template('personal/house_single.html', user=User, house=house, states=states)

@personal.route("/housinghistory/delete/<id>", methods=['GET'])
@login_required
def deletehouse(id):
    db.session.query(HousingHistory).filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('personal.housinghistory'))

@personal.route("/exportcsv", methods=['GET'])
@login_required
def exportcsv():
    import csv
    houses = db.session.query(HousingHistory).filter(HousingHistory.userid == flask_login.current_user.id).order_by(desc(HousingHistory.movein)).all()
    headings = []
    data = []
    
    headings = list(HousingHistory.__table__.columns.keys())
    headings.remove('id')
    headings.remove('update_time')
    headings.remove('date_created')
    headings.remove('userid')
    headings.insert(6,'length_of_stay')
    
    for house in houses:
        delta = relativedelta.relativedelta(house.moveout, house.movein)
        if delta.years >= 1:
            length = f'{delta.years} years, {delta.months} months'
        elif delta.years == 0 and delta.months == 1:
            length = f'{delta.months} month'
        elif delta.years == 0 and delta.months > 1:
            length = f'{delta.months} months'
        else: length = 'error'
        little = [house.movein.strftime("%m/%Y"), house.moveout.strftime("%m/%Y"), house.address, house.city, house.state, house.zip, length]
        data.append(little)
    filename = str(flask_login.current_user.firstname).lower() +'_housinghistory.csv'
    with open('website/static/'+filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headings)
        writer.writerows(data)
        f.close()
    
    full = f"static/{filename}"
    @after_this_request
    def filedelete(response):
        if os.path.exists('website/static/'+filename):
            os.remove('website/static/'+filename)
        return response
    return send_file(full, as_attachment=True)
