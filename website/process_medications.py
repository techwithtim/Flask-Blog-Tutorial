from . import db
from website.models import Medications
import datetime
from flask_login import current_user

# TODO: Finish this process with the process.txt file
def getdata():
    results = db.session.query(Medications).filter(Medications.next_refill <= datetime.datetime.now()).filter(Medications.userid == current_user.id).all()
    
    return results