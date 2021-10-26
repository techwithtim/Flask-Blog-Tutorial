from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from website.models import *
import datetime
from website import db
from sqlalchemy.sql import desc

vehicle = Blueprint("vehicle", __name__)

@vehicle.route("/vehicle", methods=['GET','POST'])
@login_required
def vehHome():
    if request.method == 'POST':
        if request.form.get('pdate') == '':
            pdate = datetime.datetime.now()
        else:
            pdate = datetime.datetime.strptime(request.form.get('pdate'), "%Y-%m-%d")
        
        if request.form.get('sdate') == '':
            sdate = datetime.datetime.now()
        else:
            sdate = datetime.datetime.strptime(request.form.get('sdate'), "%Y-%m-%d")
            
        if request.form.get('tagsexp') == '':
            tagsexp = datetime.datetime(3000, 1, 1)
        else:
            tagsexp = datetime.datetime.strptime(request.form.get('tagsexp'), "%Y-%m")
        
        newveh = Vehicles(
            name = request.form.get('name'),
            year = request.form.get('year'),
            make = request.form.get('make'),
            model = request.form.get('model'),
            trim = request.form.get('trim'),
            color = request.form.get('color'),
            purchase_date = pdate,
            sell_date = sdate,
            reasonforsale = request.form.get('reason'),
            saleamount = request.form.get('saleamt'),
            licenseplate = request.form.get('licplate'),
            purchaseprice = request.form.get('puramt'),
            purchasefrom = request.form.get('purplace'),
            vinnumber = request.form.get('vin'),
            tagsexpire = tagsexp,
            pictureURL = request.form.get('picurl'),
            curown = int(request.form.get('curown')),
        )
        db.session.add(newveh)
        db.session.commit()
    # TODO: LEFT OFF - figuring why getting error % unexpected
    from dateutil import relativedelta
    currvehs = db.session.query(Vehicles).filter(Vehicles.curown == True).all()
    ownedList = {}
    for currveh in currvehs:
        diff = relativedelta.relativedelta(currveh.sell_date, currveh.purchase_date)
        owned = f'{diff.years} years {diff.months} months {diff.days} days'
        ownedList[currveh.id] = owned
    
    vehs = db.session.query(Vehicles).order_by(desc(Vehicles.purchase_date)).all()
    return render_template('vehicles/vehicles.html', user=User, vehs=vehs, owned=ownedList)

@vehicle.route("/<id>", methods=['GET','POST'])
@login_required
def vehsingle(id):
    if request.method =="POST":
        if request.form.get('submit') == 'Add Service':
            newserv = Service(
                service = request.form.get('service'),
                place = request.form.get('place'),
                cost = request.form.get('cost'),
                mileage = request.form.get('mileage'),
                date = datetime.datetime.strptime(request.form.get('date'),"%Y-%m-%d"),
                vehiclefk = request.form.get('vehid')
            )
            db.session.add(newserv)
            db.session.commit()
            return redirect(url_for('vehicle.vehsingle', id=id))
        else:
            if request.form.get('pdate') == '':
                pdate = datetime.datetime.now()
            else:
                pdate = datetime.datetime.strptime(request.form.get('pdate'), "%Y-%m-%d")
            
            if request.form.get('sdate') == '':
                sdate = datetime.datetime.now()
            else:
                sdate = datetime.datetime.strptime(request.form.get('sdate'), "%Y-%m-%d")
                
            if request.form.get('tagsexp') == '':
                tagsexp = datetime.datetime(3000, 1, 1)
            else:
                tagsexp = datetime.datetime.strptime(request.form.get('tagsexp'), "%Y-%m")
                
            ud = db.session.query(Vehicles).filter(Vehicles.id == id).first()
            ud.name = request.form.get('name')
            ud.year = request.form.get('year')
            ud.make = request.form.get('make')
            ud.model = request.form.get('model')
            ud.trim = request.form.get('trim')
            ud.color = request.form.get('color')
            ud.purchase_date = pdate
            ud.sell_date = sdate
            ud.reasonforsale = request.form.get('reason')
            ud.saleamount = request.form.get('saleamt')
            ud.licenseplate = request.form.get('licplate')
            ud.purchaseprice = request.form.get('puramt')
            ud.purchasefrom = request.form.get('purplace')
            ud.vinnumber = request.form.get('vin')
            ud.tagsexpire = tagsexp
            ud.pictureURL = request.form.get('picurl')
            ud.curown = int(request.form.get('curown'))
            db.session.commit()
            return redirect(url_for('vehicle.vehHome'))
    
    from dateutil import relativedelta
    veh = db.session.query(Vehicles).filter(Vehicles.id == id).first()
    
    diff = relativedelta.relativedelta(veh.sell_date, veh.purchase_date)

    owned = f'{diff.years} years {diff.months} months {diff.days} days'
    services = db.session.query(Service).filter(Service.vehiclefk == id).order_by(desc(Service.date),Service.cost).all()
    return render_template('vehicles/vehicle_single.html', user=User, veh=veh, owned=owned, services=services)

@vehicle.route("/delete/<id>", methods=['GET','POST'])
@login_required
def vehdelete(id):
    db.session.query(Vehicles).filter(Vehicles.id == id).delete()
    db.session.commit()
    return redirect(url_for('vehicle.vehHome'))

@vehicle.route("/form", methods=['GET','POST'])
@login_required
def accidentform():
    if request.method == 'POST':
        driverlic = request.form.get('state') + " " + request.form.get('driverslic')
        driver = db.session.query(User).filter(User.id == request.form.get('driver')).first()
        veh = db.session.query(Vehicles).filter(Vehicles.id == request.form.get('vehicle')).first()
        ins = db.session.query(Insinfo).filter(Insinfo.id == request.form.get('insurance')).first()
        owner = db.session.query(User).filter(User.id == request.form.get('owner')).first()
        return render_template("/vehicles/accidentform.html", owner=owner, ins=ins, veh=veh, driver=driver, driverlic=driverlic)
    
    drivers = db.session.query(User).all()
    vehicles = db.session.query(Vehicles).filter(Vehicles.curown == True).all()
    insurances = db.session.query(Insinfo).all()
    owners = db.session.query(User).all()
    states = db.session.query(States).all()
    return render_template('/vehicles/preform.html', user=User, drivers=drivers, vehicles=vehicles, insurances=insurances, owners=owners, states=states)