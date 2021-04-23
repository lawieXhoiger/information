from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info.models import User
from info.modules.admin import admin_blu

@admin_blu.route("/index")
def index():
    return render_template('admin/index.html')


@admin_blu.route("/login",methods=['GET','POST'])
def login():
    """管理员登陆"""
    if request.method=='GET':
        return render_template("admin/login.html")

    username=request.form.get('username')
    password=request.form.get('password')
    # 判断参数，如果有空的话就直接直接跳转到登陆界面
    if not all([username,password]):
        return render_template('admin/login.html',errmsg='参数错误')
    # 查询当前用户
    try:
        user=User.query.filter(User.mobile==username,User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html',errmsg='用户信息查询失败')

    if not user:
        return render_template('admin/login.html', errmsg='未查询到用户')

    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='用户名或者密码错误')

    # 保存用户信息
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name
    session['is_admin'] = user.is_admin
    # 跳转到后面管理员首页   渲染模板，路由不会变，所有用 重定向
    return  redirect(url_for("admin.index"))