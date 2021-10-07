from . import db
from flask import redirect, url_for, send_file
from website.models import Facility, Medications
import datetime
from datetime import timedelta
from website.models import Projects, Tasks
from flask_login import current_user

def make_ics(filename):
    with open(filename, 'w') as my_file:
        my_file.write('BEGIN:VCALENDAR\nVERSION:2.0\n')
    
def details_ics(med, filename):
    with open (filename, 'a') as my_file:
        startdate = datetime.datetime.strftime(med.next_refill,"%Y%m%d")
        enddate = datetime.datetime.strftime(med.next_refill + timedelta(days=1),"%Y%m%d")
        MedName = med.name
        TaskName = "Call to Order " + MedName
        PickupDate = datetime.datetime.strftime(med.next_refill,"%m-%d-%Y")
        Pharmacy = db.session.query(Facility).filter(Facility.id  == med.pharmacy).first().name
        
        my_file.write('BEGIN:VEVENT\n')
        my_file.write('SUMMARY:' + TaskName +"\n")
        my_file.write('LOCATION:' + Pharmacy +"\n")
        my_file.write('DESCRIPTION:' + "Call " + Pharmacy + " to request a refill of " + MedName + " to be picked up on " + PickupDate + "\n")
        my_file.write('DTSTART;VALUE=DATE:'+ str(startdate) +"\n")
        my_file.write('DTEND;VALUE=DATE:'+ str(enddate) +"\n")
        my_file.write('END:VEVENT\n')

def close_ics(filename):
    with open (filename, 'a') as my_file:
        my_file.write('END:VCALENDAR')
    return send_file(filename, as_attachment=True)
        
        
def make_tasks(med):
    Pharmacy = db.session.query(Facility).filter(Facility.id  == med.pharmacy).first().name
    MedName = med.name
    PickupDate = med.next_refill
    Project = db.session.query(Projects).filter(Projects.name == "Medical").first().id
    
    newtask = Tasks(
        item = "Call " + Pharmacy + " to request a refill of " + MedName + " to be picked up on " + PickupDate.strftime('%m-%d-%Y'),
        userid = current_user.id,
        project = Project,
        duedate = PickupDate
    )
    db.session.add(newtask)
    db.session.commit()


def set_process_to_no(med):
    medication = db.session.query(Medications).filter(Medications.id == med.id).first()
    medication.process = False
    db.session.commit()

# TODO: Finish this process with the process.txt file

# results = db.session.query(Medications).filter(Medications.process == True).filter(Medications.userid == current_user.id).all()

# if len(results) == 0:
#     message = "No medications found to process.  Please check the process field and re-run this program"
#     print(message)
#     redirect(url_for ('views.medications_reorder'), message=message)
# else:
#     make_ics()
#     for result in results:
#         details_ics(result)
#     close_ics()
    
#     for result in results:
#         make_tasks(result)
#         set_process_to_no(result)