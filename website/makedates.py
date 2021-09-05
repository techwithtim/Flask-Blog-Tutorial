from . import db
from .models import Planner
from datetime import datetime, timedelta

def makedates(
    startdate=datetime.strftime(datetime.today(), "%Y-%m-%d"), 
    howmany=60):
    """ Use this to create more dates in the Planner table.  When the table has less than a count of 60. This program will run adding more dates to the table.

    Args:
        howmany (int): [how many new dates do you want added.  Default is 60 days]
        startdate ([type]): [the day you want the sustem to add going forward.]
    """    
    date = datetime.strptime(startdate, "%Y-%m-%d")
    for _ in range(howmany):
        plan = Planner(date = date)
        db.session.add(plan)
        db.session.commit()
        date = date + timedelta(days=1)