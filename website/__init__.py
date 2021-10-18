from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = 'website/static/images'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    app._static_folder = 'static'   
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)
    
    Migrate(app,db)

    from website.templates.views.views import views
    from website.auth import auth
    from website.templates.menu.menu import menu
    from website.templates.vehicles.vehicle import vehicle
    from website.templates.health.health import health
    from website.templates.productivity.productivity import prod
    from website.templates.personal.personal import personal
    from website.templates.settings.settings import settings

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(menu, url_prefix="/menu")
    app.register_blueprint(vehicle, url_prefix="/vehicle")
    app.register_blueprint(health, url_prefix="/health")
    app.register_blueprint(prod, url_prefix="/productivity")
    app.register_blueprint(personal, url_prefix="/personal")    
    app.register_blueprint(settings, url_prefix="/settings")



    from website.models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created database!")
