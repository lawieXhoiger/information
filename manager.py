import logging
# 数据库迁移
from flask_script import Manager
from  flask_migrate import Migrate,MigrateCommand
from info import create_app,db


# 通过指定的配置名字创建对应的app
app=create_app('development')
manager=Manager(app)

# 将app和db关联
#第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例
Migrate(app,db)
# 将迁移命令添加到manager中,
# #manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db',MigrateCommand)
#
# @app.route("/")
# def index():
#
#     return 'index'


if __name__ == "__main__":
     # app.run()

    manager.run()
