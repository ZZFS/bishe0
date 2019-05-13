from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_socketio import SocketIO, emit

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
socketio = SocketIO()


def init_ext(app):
    """ 初始化所有第三方插件 """
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    mail.init_app(app)
    socketio.init_app(app)
