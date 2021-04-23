from logging.handlers import RotatingFileHandler
import logging
from flask import Flask
from flask import g
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from flask.ext.wtf.csrf import generate_csrf
from redis import StrictRedis
from flask.ext.session import Session
from config import config

# 初始化数据库
# 在flask很多的扩展里面都可以先初始化扩展对象，然后再去调用init_app方法去初始化


db = SQLAlchemy()
# 给变量加一个注释，只是给开发人员使用的   另一中指定：redis_store:StrictRedis=None
redis_store=None #  type:StrictRedis


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
    redis_store=StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT,decode_responses=True)
    # 开启当前项目 CSRF 保护,并且可以自动对比cookie数据的scrf_token和表单里的csrf_token
    # 我们需要1.在返回响应时候往cookie中添加csrf_token
    # 2.在表单中添加一个隐藏的csrf_token,目前登录注册使用的是ajax,所以可以在
    # ajax请求的时候添加一个scrf_token
    CSRFProtect(app)
    Session(app)
    # 添加自定义过滤器

    # 添加自定义过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "index_class")

    # 捕获404页面错误
    from info.utils.common import user_login_data
    @app.errorhandler(404)
    @user_login_data
    # e接收404错误
    def page_not_fount(e):
        user=g.user
        data={
            "user":user.to_dict() if user else None
        }
        return render_template("news/404.html",data=data)

    @app.after_request
    def after_response(response):
        # 设置一个cookie
        csrf_token=generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        return response


    # 注册蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blu
    app.register_blueprint(passport_blu)

    from info.modules.news import news_blu
    app.register_blueprint(news_blu)

    from info.modules.profile import profile_blu
    app.register_blueprint(profile_blu)


    return app
