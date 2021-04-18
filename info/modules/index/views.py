from flask import current_app, jsonify
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import redis_store
from info.models import User, News, Category
from info.utils.response_code import RET

from . import index_blu

@index_blu.route("/news_list")
def news_list():
    """获取首页新闻数据"""
    # 1.获取参数,新闻的分类
    cid=request.args.get('cid','1')
    page=request.args.get('page','1')
    per_page = request.args.get('per_page', '10')

   # 2.校验参数
    try:
        page=int(page)
        cid = int(cid)
        per_page=int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="输入参数有误")

    # 3.查询数据
    filters=[]
    if cid!=1: #查询的不是最新数据

        filters.append(News.category_id==cid)
    # 查询出来的数据
    try:
        paginate=News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询错误")


    # 取到当前页的数据
    news_model_list=paginate.items    #当前数据的模型对象
    total_page=paginate.pages
    current_page=paginate.page

    news_dict_li=[]
    for news in news_model_list:
        news_dict_li.append(news.to_basic_dict())

    data={

        "news_dict_li":news_dict_li,
         "total_page":total_page,
        "current_page":current_page

    }
    return jsonify(errno=RET.OK,errmsg="输入参数有误",data=data)



@index_blu.route("/")
def index():

    """
    显示首页
    1.如果用户已经登陆,将当前用户登录的数据传到模板中,供模板显示
    :return:
    """
    # 显示用户是否登录成功的逻辑,登陆成功就显示右上角头像等信息,否则就不显示
    user_id=session.get('user_id',None)
    user=None
    if user_id:
        try:
            user=User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    news_list=[]
    # 右侧的新闻排行的逻辑
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 定义一个空字典
    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询分类数据，通过模板渲染
    categories=Category.query.all()
    category_li=[]
    for news in categories:
        category_li.append(news.to_dict())

    data={
        # 如果user是真的话就去取值前面的,如果是none就取值None
        "user":user.to_dict() if user else None,
        'news_dict_li':news_dict_li,
        "category_li":category_li

    }


    return render_template('news/index.html',data=data)

# 打开网页时候，浏览器会默认取请求根路径+/favicon.ico做网站标签的小图标
# send_static_file是flask去查指定的文件调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')