from flask import current_app
from flask import render_template
from flask import session


from info import redis_store
from info.models import User, News

from . import index_blu


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


    # 右侧的新闻排行的逻辑
    try:
        news_list=News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
    # 定义一个空字典
    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())



    data={
        # 如果user是真的话就去取值前面的,如果是none就取值None
        "user":user.to_dict() if user else None,
        'news_dict_li':news_dict_li

    }


    return render_template('news/index.html',data=data)

# 打开网页时候，浏览器会默认取请求根路径+/favicon.ico做网站标签的小图标
# send_static_file是flask去查指定的文件调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')