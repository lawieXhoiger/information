import logging
from redis import StrictRedis

class Config(object):
    # DEBUG=True
    SECRET_KEY='+hUTrmUMTP1ZtMZ1XPRe3jNDnvToMNvLo96EvT5mQx3QRh72TETgP4MzQKCQ8EUl'
    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/information27"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # 在请求结束时,如果指定此配置,数据库属性修改以后自动提交(commit)数据
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True


    REDIS_HOST='127.0.0.1'
    REDIS_PORT='6379'
    # 指定 session 保存到 redis 中
    SESSION_TYPE='redis'
    SESSION_USER_SIGNER=True
    SESSION_REDIS=StrictRedis(host=REDIS_HOST,port=REDIS_PORT)

    SESSION_PERMANENT=False
    PERMANENT_SESSION_LIFETIME=86400*2

    LOG_LEVEL=logging.DEBUG

class DevelopmentConfig(Config):
    DEBUG = True



class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    DEBUG = True
    TESTING=True


config={
    "development":DevelopmentConfig,
    "production":ProductionConfig,
    "testing":TestingConfig
}