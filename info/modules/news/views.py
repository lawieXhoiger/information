from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info.models import User, News
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route("/news_collect",methods=['POST'])
@user_login_data
def collect_news():
    """
    收藏新闻
    1.接收参数
    2.判断参数
    3.查询新闻
    :return:
    """
    user = g.user
    news_id=request.json.get("news_id")
    action =request.json.get("action")
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id=int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action=='cancel_collect':
        if news in user.collection_news:
            user.collect_news.remove(news)
    else:
        # 收藏
        if news not in user.collection_news:
            user.collect_news.append(news)


    return jsonify(errno=RET.OK, errmsg="收藏成功")




@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :return:
    """

    user = g.user
    news_list = []
    # 右侧的新闻排行的逻辑
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 定义一个空字典

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询新闻数据
    news=None
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        # 404错误,后续统一处理
        abort(404)

    # TODO收藏
    is_collected=False

    news.clicks += 1
    # 如果用户已登陆,就判断新闻是否在被用户收藏的列表中
    if user:
        if news in user.collection_news:
            is_collected=True

    data = {
        # 如果user是真的话就去取值前面的,如果是none就取值None
        "user": user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'news':news.to_dict(),
        'is_collected':is_collected
    }
    # 更新新闻点击次数

    return render_template("news/detail.html",data=data)