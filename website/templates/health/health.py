from operator import or_
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, after_this_request
from flask.templating import render_template_string
from flask_login import login_required

from website.models import *
from flask_mail import Message
from datetime import datetime, timedelta
from dateutil import relativedelta
from website import db, mail
import css_inline, html2text


from subprocess import run, PIPE
from sqlalchemy.sql import func, desc, or_
from website.vfc_maker import make_vfc
import datetime, sys, flask_login, os
from math import ceil
from website.process_medications import *

health = Blueprint("health", __name__)

#Health
@health.route("/health", methods=['GET'])
# @login_required
def healthHome():
    return render_template("health/health.html", user=User)

@health.route("/doctors", methods=['GET', 'POST'])
@login_required
def doctors():
    if request.method == 'POST':
        newdr = Doctor(
            name=request.form.get('drname').title(), 
            facilityfk=request.form.get('facility'), 
            userid=request.form.get('thisuserid'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip=request.form.get('zip'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            asst=request.form.get('asst')
            )
        db.session.add(newdr)
        db.session.commit() 
    
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).order_by(Doctor.facilityfk, Doctor.name).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).all()
    return render_template("health/doctors.html", user=User, doctors=doctors, facilities=facilities)

@health.route("/facilities", methods=['GET', 'POST'])
@login_required
def facilities():
    if request.method == 'POST':
        newfac = Facility(
            name=request.form.get('name'),
            address=request.form.get('addy'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip=request.form.get('zip'),
            phone=request.form.get('phone'),
            type = request.form.get('type'),
            userid = request.form.get('thisuserid')
            )
        
        db.session.add(newfac)
        db.session.commit()
        
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).order_by(Facility.type, Facility.name).all()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).all()
    return render_template("health/facilities.html", user=User, facilities=facilities, doctors=doctors)

@health.route("/edit_facilities/<id>", methods=['GET', 'POST'])
@login_required
def editfacilities(id):
    facility = db.session.query(Facility).filter(Facility.id == id).first()
    if request.method == 'POST':
        facility.name = request.form.get('name')
        facility.address=request.form.get('addy')
        facility.city=request.form.get('city')
        facility.state=request.form.get('state')
        facility.zip=request.form.get('zip')
        facility.phone=request.form.get('phone')
        facility.type = request.form.get('type')
        facility.userid = request.form.get('thisuserid')
        db.session.commit()
        return redirect(url_for('health.facilities'))
        
    return render_template("health/editfacilities.html", user=User, facility=facility)


@health.route("/surgeries", methods=['GET', 'POST'])
@login_required
def surgeries():
    if request.method == 'POST':
        
        def calculateAge(startdate):
            bday = flask_login.current_user.dob
            age = startdate.year - bday.year
            return age
     
        newsurg = Surgeries(
            name = request.form.get('name'),
            startdate= datetime.datetime.strptime(request.form.get('sdate'),"%Y-%m-%d"),
            description= request.form.get('desc'),
            body_part= request.form.get('bodypart'),
            age = calculateAge(datetime.datetime.strptime(request.form.get('sdate'),"%Y-%m-%d")),
            doctorfk= request.form.get('doctor'),
            facilityfk= request.form.get('facility'),
            userid= request.form.get('thisuserid')
        )
        db.session.add(newsurg)
        db.session.commit()
    
    surgeries = db.session.query(Surgeries).filter(Surgeries.userid == flask_login.current_user.id).order_by(desc(Surgeries.startdate)).all()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).order_by(Doctor.name).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type != "Pharmacy").order_by(Facility.name).all()
    return render_template("health/surgeries.html", user=User, facilities=facilities, doctors=doctors, surgeries=surgeries)

@health.route("/hospital", methods=['GET', 'POST'])
@login_required
def hospital():
    if request.method == 'POST':
        newhosp = Hosptial(
            datestart = datetime.datetime.strptime(request.form.get('sdate'),("%Y-%m-%d")),
            dateend = datetime.datetime.strptime(request.form.get('edate'),("%Y-%m-%d")),
            reason = request.form.get('reason'),
            doctorfk = request.form.get('doctor'),
            facilityfk = request.form.get('facility'),
            userid = flask_login.current_user.id
        )
        db.session.add(newhosp)
        db.session.commit()
    
    stays = db.session.query(Hosptial).filter(Hosptial.userid == flask_login.current_user.id).order_by(desc(Hosptial.datestart)).all()
    LOS = []
    for stay in stays:
        delta = relativedelta.relativedelta(stay.dateend, stay.datestart)
        if delta.months >= 1:
            length = f'{delta.months} months, \n{delta.weeks} weeks, \n{delta.days-(delta.weeks*7)} days'
        elif delta.months == 0 and delta.weeks >= 1:
            length = f'{delta.weeks} weeks, {delta.days-(delta.weeks*7)} days'
        elif delta.months == 0 and delta.weeks == 0:
            length = f'{delta.days} days'
        else: length = 'error'
        little = {}
        little['id'] = stay.id
        little['stay'] = length
        LOS.append(little)
        
        
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).order_by(Doctor.facilityfk).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type == "Hosptial").order_by(Facility.type, Facility.name).all()
    return render_template("health/hospital.html", user=User, stays=stays, doctors=doctors, facilities=facilities, los=LOS)

@health.route("/hospital/delete/<id>", methods=['GET', 'POST'])
@login_required
def hospital_delete(id):
    db.session.query(Hosptial).filter(Hosptial.id == id).delete()
    db.session.commit()
    return redirect(url_for('health.hospital'))

@health.route("/hospital/<id>", methods=['GET', 'POST'])
@login_required
def hospital_update(id):
    if request.method == 'POST':
       udstay = db.session.query(Hosptial).filter(Hosptial.id == id).first()
       udstay.datestart = datetime.datetime.strptime(request.form.get('sdate'),"%m/%d/%Y")
       udstay.dateend = datetime.datetime.strptime(request.form.get('edate'),"%m/%d/%Y")
       udstay.reason = request.form.get('reason')
       udstay.doctorfk = request.form.get('doctor')
       udstay.facilityfk = request.form.get('facility')
       udstay.userid = flask_login.current_user.id
       db.session.commit()
       return redirect(url_for('health.hospital'))
                       
    stay = db.session.query(Hosptial).filter(Hosptial.id == id).first()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).order_by(Doctor.facilityfk).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type == "Hosptial").order_by(Facility.type, Facility.name).all()
    return render_template('health/hospital_update.html', user=User, stay=stay, doctors=doctors, facilities=facilities)

@health.route("/medications", methods=['GET', 'POST'])
@login_required
# TODO: Make it so the user can know when the medication is due to be refilled.
# FIXME: Create a 8.5 x 11 report in pdf to print out. (made report medlist.html.  Need to get it to print with pdfkit)
def medications():
    if request.method == 'POST':
        # if request.form['exportPDF'] == 'exportPDF':
        #     pdfkit.from_url("http://127.0.0.1:5000"+url_for('health.medlistPrint'), 'medlist-'+flask_login.current_user.firstname+' '+flask_login.current_user.lastname+'.pdf')
        #     render_template(url_for('health.medications'))
        
        lastrefill = datetime.datetime.strptime(request.form.get('lastordered'),"%Y-%m-%d")
        numfilleddays=request.form.get('num_filled_days')

        newmed = Medications(
            name=request.form.get('name').title(),
            dose=request.form.get('dose'),
            how_often=request.form.get('howoften'),
            num_filled_days=request.form.get('num_filled_days'),
            reason_for_taking=request.form.get('reason_for_taking'),
            pharmacy=request.form.get('pharm'),
            last_refilled = lastrefill,
            next_refill = lastrefill + datetime.timedelta(days=int(numfilleddays)),
            userid=request.form.get('thisuserid'),
            doctorfk=request.form.get('doctor')
            )
        db.session.add(newmed)
        db.session.commit()
    
    pharmacy = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type == "Pharmacy").all()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).all()
    medications = db.session.query(Medications).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.next_refill, Medications.name).all()
    return render_template("health/medications.html", user=User, facilities=facilities, doctors=doctors, pharmacy=pharmacy, medications=medications)

@health.route('/medupdate/<id>', methods=['GET', 'POST'])
@login_required
def medupdate(id):
    if request.method == 'POST':
        print(request.form.get('howoften'))
        lastrefill = datetime.datetime.strptime(request.form.get('lastordered'),"%Y-%m-%d")
        med = db.session.query(Medications).filter(Medications.id == id).first()
        med.name = request.form.get('name')
        med.dose = request.form.get('dose')
        med.how_often = request.form.get('howoften')
        med.reason_for_taking = request.form.get('reason_for_taking')
        med.last_refilled = lastrefill
        med.next_refill = lastrefill + datetime.timedelta(days=int(request.form.get('num_filled_days')))
        med.num_filled_days = request.form.get('num_filled_days')
        med.doctorfk = request.form.get('doctor')
        med.pharmacy = request.form.get('rx')
        db.session.commit()
        return redirect(url_for('health.medications'))
    meds = db.session.query(Medications).filter(Medications.id == id).first()
    pharm = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type == "Pharmacy").all()
    doctors = db.session.query(Doctor).filter(Doctor.userid ==flask_login.current_user.id).order_by(Doctor.name).all()
    return render_template("health/medupdate.html", user=User, meds=meds, pharms=pharm, doctors=doctors)

@health.route("/medications/reorder", methods=['GET', 'POST'])
@login_required
def medications_reorder():
    referrer = request.referrer
    def reorder_meds(id, med, dose, howoften, days, reason, pharm, doctor, lastrefill):
        meds = db.session.query(Medications).filter(Medications.id == id).first()
        meds.name = med
        meds.dose = dose
        meds.how_often = howoften
        meds.num_filled_days = days
        meds.reason_for_taking = reason
        meds.pharmacy = pharm
        meds.doctorfk = doctor
        meds.last_refilled = lastrefill
        meds.next_refill = lastrefill + timedelta(days=int(days))
        meds.process = True
        db.session.commit()
        

    if request.method == 'POST':
        if request.form.get('process') == 'PROCESS MEDICATIONS':
            path = os.path.dirname(os.path.abspath(__file__))
            filename = "ics.ics"
            fullname = os.path.join(path,filename)
            results = db.session.query(Medications).filter(Medications.process == True).filter(Medications.userid == flask_login.current_user.id).all()
            cal = request.form.get('calendar')
            if len(results) == 0:
                message = "No medications found to process.  Please check the process field and re-run this program"
                print(message)
                redirect(url_for ('health.medications_reorder'), message=message)
            else:
                make_ics(fullname, cal)
                for result in results:
                    details_ics(result,fullname)
                close_ics(path,filename,fullname)
                
                for result in results:
                    make_tasks(result)
                    set_process_to_no(result)
                print('Done!')
            @after_this_request
            def filedelete(response):
                if os.path.exists(fullname):
                    os.remove(fullname)
                return response
        
        else:
            reorder = request.form.getlist('reorder')
            id = request.form.getlist('id')
            med = request.form.getlist('med')
            dose = request.form.getlist('dose')
            howoften = request.form.getlist('how_often')
            days = request.form.getlist('num_filled_days')
            reason = request.form.getlist('reason_for_taking')
            pharm = request.form.getlist('pharmacy')
            doctor = request.form.getlist('doctorfk')
            lastrefill = request.form.get('reorder_date')
            
            for i in range(len(id)):
                if reorder[i] == "Yes":
                    reorder_meds(
                        id[i], 
                        med[i], 
                        dose[i], 
                        howoften[i],
                        days[i], 
                        reason[i], 
                        pharm[i], 
                        doctor[i], 
                        datetime.datetime.strptime(lastrefill,"%Y-%m-%d")
                        )
            return redirect(referrer)
        return send_file(fullname, as_attachment=True)
    pharmacy = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(Facility.type == "Pharmacy").all()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).all()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).all()
    medications = db.session.query(Medications).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.next_refill, Medications.name).all()
    return render_template("health/medications_reorder.html", user=User, facilities=facilities, doctors=doctors, pharmacy=pharmacy, medications=medications, ref=referrer)

@health.route("/cpap", methods=['GET','POST'])
@login_required
def cpap():
    if request.method == "POST":
        lastordered = datetime.datetime.strptime(request.form.get('lastordered'),"%Y-%m-%d")
        nextorder = lastordered + timedelta(days = int(request.form.get('howoften')))
        newsupply = Cpap(
            name = request.form.get('name'),
            itemnum = request.form.get('itemnum'),
            howoften = request.form.get('howoften'),
            lastordered = lastordered,
            nextorderdate = nextorder,
            imageURL = request.form.get('imageURL'),
            userid = request.form.get('thisuserid')
        ) 
        db.session.add(newsupply)
        db.session.commit()
        return redirect(url_for('health.cpap'))
    
    cntCpap = db.session.query(Cpap).filter(Cpap.nextorderdate <= datetime.datetime.now()+timedelta(days=5)).filter(Cpap.userid == flask_login.current_user.id).count()
    if cntCpap != 0:
        cpaps = db.session.query(Cpap).filter(Cpap.nextorderdate <= datetime.datetime.now()+timedelta(days=5)).filter(Cpap.userid == flask_login.current_user.id).all()
        template = render_template('/emails/reorder_cpap.html', user=User, cpaps=cpaps)
        inlined = css_inline.inline(template)
        msg = Message()
        msg.subject = 'CPAP order for ' + flask_login.current_user.firstname + " " + flask_login.current_user.lastname
        msg.sender = flask_login.current_user.email
        msg.recipients = ['paul@mailtrap.io', 'rbtm2006@me.com']
        msg.html = inlined
        msg.body = html2text.html2text(inlined)
        mail.send(msg)

    cpaps = db.session.query(Cpap).filter(Cpap.userid == flask_login.current_user.id).order_by(Cpap.nextorderdate).all()
    return render_template("health/cpap.html", user=User, cpaps=cpaps)

@health.route("/cpap/delete/<id>", methods=['GET'])
@login_required
def deletecpap(id):
    Cpap.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.cpap'))

@health.route("/cpap/<id>", methods=['GET', 'POST'])
@login_required
def updatecpap(id):
    if request.method == "POST":
        lastordered = datetime.datetime.strptime(request.form.get('lastordered'),"%Y-%m-%d")
        nextorder = lastordered + timedelta(days = int(request.form.get('howoften')))
        
        cpap = db.session.query(Cpap).filter_by(id=id).first()
        cpap.name = request.form.get('name'),
        cpap.lastordered = lastordered
        cpap.nextorderdate = nextorder
        cpap.howoften = request.form.get('howoften')
        cpap.imageURL = request.form.get('imageURL')
        cpap.itemnum = request.form.get('itemnum')
        db.session.commit()
        
        return redirect(url_for('health.cpap'))
    
    cpap = Cpap.query.filter_by(id=id).first()
    return render_template('health/cpap_single.html', user=User, cpap=cpap)

@health.route("/deletingMed/<id>")
@login_required
def deleteMed(id):
    Medications.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.medications'))

@health.route("/deletingFacility/<id>")
@login_required
def deleteFacility(id):
    Facility.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.facilities'))

@health.route("/deletingDoctors/<id>")
@login_required
def deleteDoctors(id):
    Doctor.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.doctors'))

@health.route("/allergies", methods=['GET', 'POST'])
@login_required
def allergies():
    if request.method == 'POST':
        allergic = Allergies(
            name=request.form.get('name').title(),
            reaction = request.form.get('reaction'),
            dateadded = datetime.datetime.strptime(request.form.get('dateadded'),"%Y-%m-%d"),
            userid=request.form.get('thisuserid')
            )
        db.session.add(allergic)
        db.session.commit()
    
    allergies = db.session.query(Allergies).filter(Allergies.userid ==flask_login.current_user.id).order_by(desc(Allergies.dateadded), Allergies.name).all()
    return render_template("health/allergies.html", user=User, allergies=allergies)

@health.route("/deletingAllergy/<id>")
@login_required
def deletingAllergy(id):
    Allergies.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.allergies'))

@health.route("/a1c", methods=['GET', 'POST'])
@login_required
def a1c():
    if request.method == "POST":
        newresult = A1C(
            date = datetime.datetime.strptime(request.form.get('testdate'), "%Y-%m-%d"),
            testresult = request.form.get('testresult'),
            userid = request.form.get('thisuserid'),
            doctorfk = request.form.get('doctor')
        )
        db.session.add(newresult)
        db.session.commit()
        
    results = db.session.query(A1C).filter(A1C.userid == flask_login.current_user.id).order_by(desc(A1C.date)).all()
    
    labels = []
    dataset = []
    for result in results:
        label = result.date.strftime("%m/%y")
        data = result.testresult
        labels.append(label)
        dataset.append(data)

    
    currentvalue = db.session.query(func.max(A1C.date).label('ld'), A1C.testresult, A1C.userid).filter(A1C.userid == flask_login.current_user.id).order_by(A1C.date).first()
    if currentvalue.testresult is None:
        eag=0
    else:
        eag = ceil(28.7 * currentvalue.testresult - 46.7)
    
    doctors = db.session.query(Doctor).filter(Doctor.userid ==flask_login.current_user.id).order_by(Doctor.name).all()
    return render_template("/health/a1c.html", user=User, results=results, currentvalue=currentvalue, doctors=doctors, eag=eag, labels=labels, dataset=dataset)

@health.route("/doctor/card/<id>", methods=['GET'])
def makeCard(id): 
    doctorinfo = db.session.query(Doctor.name, Doctor.address, Doctor.city, Doctor.state, Doctor.zip, Doctor.phone, Doctor.email, Facility.name.label('company')).filter(Doctor.id == id).join(Facility,Facility.id == Doctor.facilityfk).first()
    filename = make_vfc(doctorinfo)
    
    @after_this_request
    def deletefile(response):
        if os.path.exists("website/"+filename):
            os.remove("website/"+filename)
        return response
    return send_file(filename, attachment_filename=filename)
    
@health.route("/doctors/edit/<id>", methods=['GET', 'POST'])
@login_required
def doctorsEdit(id):
    if request.method == 'POST':
        editDr = db.session.query(Doctor).filter(Doctor.id == id).first()
        editDr.name=request.form.get('drname').title()
        editDr.facilityfk=request.form.get('facility')
        editDr.userid=request.form.get('thisuserid')
        editDr.address=request.form.get('address')
        editDr.city=request.form.get('city')
        editDr.state=request.form.get('state')
        editDr.zip=request.form.get('zip')
        editDr.phone=request.form.get('phone')
        editDr.email=request.form.get('email')
        editDr.asst=request.form.get('asst')
        db.session.commit()
        return redirect(url_for('health.doctors'))
        
    doctors = db.session.query(Doctor).filter(Doctor.id == id).first()
    facilities = db.session.query(Facility).filter(Facility.userid == flask_login.current_user.id).filter(or_(Facility.type == 'Clinic', Facility.type == 'Hosptial')).all()
    return render_template("health/doctorsEdit.html", user=User, doctors=doctors, facilities=facilities)

@health.route("/medlist", methods=['GET'])
def medlistPrint():
    medications = db.session.query(Medications).filter(Medications.userid == flask_login.current_user.id).order_by(Medications.reason_for_taking,Medications.name).all()
    doctors = db.session.query(Doctor).filter(Doctor.userid == flask_login.current_user.id).order_by(Doctor.name).all()
    return render_template("health/medicationlist.html", user=User, medications=medications, doctors=doctors)

@health.route("/a1c/delete/<id>")
@login_required
def deleteA1C(id):
    A1C.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.a1c'))

@health.route("/surgery/delete/<id>")
@login_required
def deleteSurg(id):
    Surgeries.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('health.surgeries'))

@health.route("/allergy/<id>", methods=["GET","POST"])
@login_required
def allergy_edit(id):
    if request.method == 'POST':
        item = db.session.query(Allergies).filter_by(id=id).first()
        item.name = request.form.get('name')
        item.reaction = request.form.get('reaction')
        item.dateadded = datetime.datetime.strptime(request.form.get('dateadded'),"%Y-%m-%d")
        db.session.commit()
        return redirect(url_for('health.allergies'))
    
    allergy = db.session.query(Allergies).filter_by(id=id).first()
    return render_template('health/allergies_edit.html', user=User, allergy=allergy )
