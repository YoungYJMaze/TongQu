# -*- coding: UTF-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
from flask_socketio import SocketIO
import eventlet
from werkzeug.contrib.fixers import LighttpdCGIRootFix

eventlet.monkey_patch()
socketio = SocketIO()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from app.models import User
from app.models import load_user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name):
    app = Flask(__name__)
    app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    socketio.init_app(app, engineio_logger=True, async_mode='eventlet')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix='/chat')
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app


