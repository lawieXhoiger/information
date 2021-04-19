from flask import current_app
from flask import g
from flask import render_template
from flask import session

from info.models import User, News
from info.modules.news import news_blu
from info.utils.common import user_login_data


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :return:
    """


    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #
    # news_list = []
    # # 右侧的新闻排行的逻辑
    # try:
    #     news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    # except Exception as e:
    #     current_app.logger.error(e)
    # 定义一个空字典
    user=g.user
    news_list=[]
    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())


    data = {
        # 如果user是真的话就去取值前面的,如果是none就取值None
        "user": user.to_dict() if user else None,
        'news_dict_li': news_dict_li,

    }

    return render_template("news/detail.html",data=data)