from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect
from redis import StrictRedis
from flask.ext.session import Session


from config import config

# 在init创建app并进行配置
app = Flask(__name__)
# 加载配置
app.config.from_object(config['development'])


# 初始化数据库
db=SQLAlchemy(app)
# 初始化redis存储对象
redis_store=StrictRedis(host=config['development'].REDIS_HOST,port=config['development'].REDIS_PORT)
# 开启当前项目 CSRF 保护
CSRFProtect(app)
Session(app)
