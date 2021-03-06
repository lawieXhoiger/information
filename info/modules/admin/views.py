import time
from datetime import datetime, timedelta

from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info import constants
from info.models import User, News
from info.modules.admin import admin_blu


# 如果不是管理员不能访问管理员的权限
from info.utils.common import user_login_data


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """新闻审核"""
    news=None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template('admin/news_review_detail.html',data={"errmsg":"未查询到此新闻"})

    data={
        'news':news.to_dict()
    }
    return render_template('admin/news_review_detail.html',data=data)



@admin_blu.route('/news_review')
def news_review():
    """返回待审核新闻列表"""

    page = request.args.get("p", 1)
    keywords = request.args.get("keywords", "")

    try:

        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1
    try:
        filters = [News.status != 0]
        if keywords:
            # 如果关键字存在，就 添加关键词的检索选项
            filters.append(News.title.contains(keywords))
        # 查询审核未通过的  创建时间以最新的来排
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_review_dict())

    context = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_li": news_dict_li  }

    return render_template('admin/news_review.html',data=context)



@admin_blu.route('/user_list')
def user_list():
    """获取用户列表"""
    # 设置变量默认值
    page = request.args.get('p', 1)
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)

    current_page = 1
    total_page = 1
    user_list=[]
    try:
        paginate = User.query.filter(User.is_admin==False).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        current_page = paginate.page
        total_page = paginate.pages
        user_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for user in user_list:
        user_dict_li.append(user.to_admin_dict())
    context = {
        "total_page": total_page,
        "current_page": current_page,
        "user_dict_li": user_dict_li}
    return render_template('admin/user_list.html',data=context)



@admin_blu.route("/user_count")
def user_count():
    # 年新增数
    total_count = 0
    try:
        total_count=User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数
    mon_count=0
    t=time.localtime()
    # 月增长人数是：开始创建的时间 > 当月第一天零点零分零秒的时间
    begin_mon_date=datetime.strptime(('%d-%02d-01')%(t.tm_year,t.tm_mon),"%Y-%m-%d")
    try:
        mon_count = User.query.filter(User.is_admin == False,User.create_time>begin_mon_date).count()
    except Exception as e:
        current_app.logger.error(e)


    # 日新增数
    day_count=0
    begin_day_date = datetime.strptime(('%d-%02d-%02d') % (t.tm_year, t.tm_mon,t.tm_mday), "%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > begin_day_date).count()
    except Exception as e:
        current_app.logger.error(e)


    # 折线图数据
    active_time=[]
    active_count=[]

    today_date = datetime.strptime(('%d-%02d-%02d') % (t.tm_year, t.tm_mon, t.tm_mday), "%Y-%m-%d")
    for i in range(0,31):
        # 取到某一天的零点零分
        begin_date = today_date-timedelta(days=i)
        end_date = today_date-timedelta(days=(i-1))
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime("%Y-%m-%d"))

    # 活跃时间安装从小到大排序
    active_time.reverse()
    active_count.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_time":active_time,
        "active_count":active_count
    }
    return render_template('admin/user_count.html',data=data)



@admin_blu.route("/index")
@user_login_data
def index():
    user=g.user
    return render_template('admin/index.html',user=user.to_dict())


@admin_blu.route("/login",methods=['GET','POST'])
def login():
    """管理员登陆"""
    if request.method=='GET':
        user_id=session.get('user_id',None)
        is_admin = session.get('is_admin',False)
        if user_id and is_admin: #如果之前有管理员登陆信息存在，就直接跳转到后台登陆页
            return redirect(url_for('admin.index'))
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