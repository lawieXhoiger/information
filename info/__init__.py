
from logging.handlers import RotatingFileHandler

import logging
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from flask.ext.session import Session
from config import config


from info.modules.index import index_blu

# 初始化数据库
# 在flask很多的扩展里面都可以先初始化扩展对象，然后再去调用init_app方法去初始化
db = SQLAlchemy()
redis_store=None
def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)



# create_app相当于工厂方法
def create_app(config_name):
    # 配置日志,并且传入配置名字，以便能获取到指定配置所对应的日志等级
    setup_log(config_name)
    # 在init创建app并进行配置
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 初始化app
    db.init_app(app)

    global redis_store
    # 初始化redis存储对象,缓存的数据用到redis_store
    redis_store=StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    # 开启当前项目 CSRF 保护
    CSRFProtect(app)
    Session(app)

    # 注册蓝图
    app.register_blueprint(index_blu)

    return app
