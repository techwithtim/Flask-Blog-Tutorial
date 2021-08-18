from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import User

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("home.html", user=User)

@views.route("/cpap")
@login_required
def cpap():
    cpapsupplies = ['one', 'two', 'three', 'four', 'five']
    return render_template("cpap.html", user=User, supplies = cpapsupplies)