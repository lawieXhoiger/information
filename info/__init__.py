from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from flask.ext.session import Session
from config import config
# 初始化数据库
# 在flask很多的扩展里面都可以先初始化扩展对象，然后再去调用init_app方法去初始化
db = SQLAlchemy()

# create_app相当于工厂方法
def create_app(config_name):
    # 在init创建app并进行配置
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 初始化app
    db.init_app(app)


    # 初始化redis存储对象
    redis_store=StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    # 开启当前项目 CSRF 保护
    CSRFProtect(app)
    Session(app)
    return app
