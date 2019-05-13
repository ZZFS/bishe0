import random

from flask import Flask, session

from App.admainView import admin
from App.ext import init_ext
from App.itemView import item
from App.settings import envs
from App.userView import user

app = Flask(__name__, template_folder=settings.TEMPLATE_FOLDER, static_folder=settings.static_folder)
# 初始化配置   从setting.py中加载配置
app.config.from_object(settings.envs.get('develop'))


def create_app():
    # 注册蓝图，初始化蓝图
    app.register_blueprint(blueprint=user, url_prefix='/user')
    app.register_blueprint(blueprint=admin, url_prefix='/admin')
    app.register_blueprint(blueprint=item, url_prefix='/item')
    # 初始化第三方插件，库
    init_ext(app)
    return app


