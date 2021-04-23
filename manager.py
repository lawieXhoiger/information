import logging
# 数据库迁移
from flask_script import Manager
from  flask_migrate import Migrate,MigrateCommand
from info import create_app,db,models
# 通过指定的配置名字创建对应的app
app=create_app('development')
manager=Manager(app)

from info.models import User
# 将app和db关联
#第一个参数是Flask的实例，第二个参数是Sqlalchemy数据库实例

Migrate(app,db)
# 将迁移命令添加到manager中,
# #manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
manager.add_command('db',MigrateCommand)

# 把函数改做命令行
@manager.option('-n','-name',dest='name')
@manager.option('-p','-password',dest='password')
def create_super_user(name,password):
    if not all([name,password]):
        print("参数不足")

    user = User()
    user.nick_name=name
    user.mobile=name
    user.password=password
    user.is_admin=True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    print('添加成功')

if __name__ == "__main__":
     # app.run()

    manager.run()
