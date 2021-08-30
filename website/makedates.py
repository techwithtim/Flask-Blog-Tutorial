from . import db
from .models import Planner
from datetime import datetime, timedelta

def makedates():
    date = datetime.today()
    for _ in range(365):
        plan = Planner(date = date)
        db.session.add(plan)
        db.session.commit()
        date = date + timedelta(days=1)
    