from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants, db
from info.models import User, News, Comment, CommentLike
from info.modules.news import news_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


@news_blu.route('/comment_like',methods=["POST"])
@user_login_data
def comment_like():
    """
    新闻点赞
    :return:
    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    comment_id=request.json.get("comment_id")

    if not all([comment_id, news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("add", "remove"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")


    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论数据不存在")

    if action=='add':
        #点赞评论
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if not comment_like:
            comment_like = CommentLike()
            comment_like.comment_id = comment_id
            comment_like.user_id = g.user.id
            db.session.add(comment_like)
            # 增加点赞条数
            comment.like_count += 1

    else:
        #取消点赞
        comment_like = CommentLike.query.filter_by(comment_id=comment_id, user_id=g.user.id).first()
        if comment_like:
            db.session.delete(comment_like)
            # 减小点赞条数
            comment.like_count -= 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库操作失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")




@news_blu.route('/news_comment',methods=["POST"])
@user_login_data
def comment_news():
    """
    评论新闻或者回复评论

    """
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    news_id=request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id=request.json.get("parent_id")

    if not all([news_id,comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id=int(news_id)
        if parent_id:
            parent_id=int(parent_id)
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

    # 初始化一个评论模型,并且复制
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
       comment.parent_id=parent_id
    # 因为在return的时候需要用到comment的id,而这些是return之后才执行的commit
    # 所有需要自己commit
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

        # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())



@news_blu.route("/news_collect",methods=["POST"])
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

    if not all([news_id,action]) :
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "cancel_collect"]:
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
            user.collection_news.remove(news)

    else:
        # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)


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

    #  定义一个空字典

    news_dict_li= []
    for news in  news_list:
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
    #  更新新闻的点击次数
    news.clicks += 1
    # TODO收藏
    is_collected=False


    # 如果用户已登陆,就判断新闻是否在被用户收藏的列表中
    if user:
        if news in user.collection_news:
            is_collected=True

    # 查询评论新闻
    comments = []
    try:  #获取当前所有的评论数据
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    # 需求:查询出当前用户在当前新闻里面都点赞了那些评论  comment
    # 1.查询出当前新闻的所有评论,取出评论的Id  commentlike & commentlike.user_id=user.id
    # 2.在查询出当前评论中有哪些是被当前用户所点赞的
    comment_like_ids=[]
    if  user:
        try:
            comment_ids=[comment.id for comment in comments]
            comment_likes=CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),CommentLike.user_id==user.id).all()
        # 3.取到所有被点赞的评论id      在所有的被点赞的评论中查询出当前评论被点赞的评论id
            comment_like_ids=[comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)


    comment_dict_li= []
    for comment in comments:
        comment_dict = comment.to_dict() # 返回每个评论的里面的id等一些信息
        # 代表没有点赞
        comment_dict["is_like"]=False
        # 判断当前遍历的评论里是否被当前登陆用户所点赞
        if comment.id in comment_like_ids:
            comment_dict["is_like"] = True
        comment_dict_li.append(comment_dict)

    data = {
        # 如果user是真的话就去取值前面的,如果是none就取值None
        "user": user.to_dict() if user else None,
        'news_dict_li': news_dict_li,
        'news':news.to_dict(),
        'is_collected':is_collected,
        'comments':comment_dict_li
    }


    return render_template("news/detail.html",data=data)