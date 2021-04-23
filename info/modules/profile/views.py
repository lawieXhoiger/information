from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.constants import QINIU_DOMIN_PREFIX
from info.models import Category, News
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from info.utils.response_code import RET


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():
    page=request.args.get('p',1)
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page=1

    user=g.user
    # 查询用户收藏的新闻
    news_list=[]
    current_page = 1
    total_page = 1
    try:
        paginate=News.query.filter(News.user_id==user.id).paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
        news_list=paginate.items
        current_page=paginate.page
        total_page=paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_review_dict())

    data={
        "news_dict_li":news_dict_li,
        "current_page":current_page,
        "total_page":total_page
    }

    return render_template('news/user_news_list.html',data=data)


@profile_blu.route('/news_release',methods=['GET','POST'])
@user_login_data
def news_release():
    """新闻发布"""
    if request.method=='GET':

        categories = []
        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li=[]
        for category in categories:
            category_dict_li.append(category.to_dict())
        category_dict_li.pop(0)
        data={
            "categories":category_dict_li
        }
        return render_template('news/user_news_release.html',data=data)

    # 1. 获取要提交的数据
    title = request.form.get("title")
    # print(title)
    source = "个人发布"
    # 新闻摘要
    digest = request.form.get("digest")
    # 新闻内容
    content = request.form.get("content")
    # 索引图片
    index_image = request.files.get("index_image")
    # 分类id
    category_id = request.form.get("category_id")
    # 1.校验：判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    try:
        category_id=int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")


    try:
        # 尝试取到图片，并且校验图片
        index_image = index_image.read()
        key = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 校验正确以后，往数据库开始传值
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态，0是审核通过，1是审核中，-1是审核不通过
    news.status = 1

    # 4. 保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    """我的收藏界面的渲染"""
    # 获取参数，页数
    page=request.args.get('p',1)
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 查询用户指定页数的收藏新闻

    user=g.user
    try:
        paginate=user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
        current_page=paginate.page  # 当前页
        total_page=paginate.pages  #总页数
        news_list=paginate.items  #当前数据的模型对象
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询错误")

    news_dict_li=[]
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data={
        "current_page":current_page,
        "total_page":total_page,
        "news_dict_li":news_dict_li
    }


    return render_template('news/user_collection.html',data=data)


@profile_blu.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    """修改密码界面的渲染"""
    if request.method == "GET":
        return render_template('news/user_pass_info.html')
    # 获取参数：旧密码和新密码
    old_password=request.json.get('old_password')
    new_password=request.json.get('new_password')

    # 判断参数是否存在
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    # 判断旧密码是否正确
    user=g.user
    if not user.check_password(old_password):
        return jsonify(errno=RET.PWDERR,errmsg="原密码错误")


    # 设置新密码
    user.password=new_password

    # # 校验新密码是否正码,在前端对比
    # if not user.check_password(new_password):
    #     return jsonify(errno=RET.PWDERR,errmsg="原密码错误")

    return jsonify(errno=RET.OK,errmsg="保存成功")


@profile_blu.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    """上传图片"""
    user = g.user
    # （1）get请求渲染页面
    if request.method == "GET":
        return render_template('news/user_pic_info.html',data={"user": user.to_dict()})

    # （2）post请求的话，读取修改用户的头像信息
    # ①取到上传的图片名字
    try:
        avatar=request.files.get('avatar').read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        # ②使用自己封装的storage方法去进行图片的上传（用的七牛云）
        key=storage(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    # ③保存头像地址  ,数据库存前半段地址，可以节省空间
    user.avatar_url=key
    return jsonify(errno=RET.OK,errmsg="OK",data={"avatar_url":QINIU_DOMIN_PREFIX+key})


@profile_blu.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    """
    用户的基本信息
    1.获取用户的登录信息,渲染模板
    2.获取用户所需所有的参数并进行判断
    3.更新并保存数据
    4.返回结果
    :return:
    """
    # 1.获取用户的登录信息,渲染模板
    user = g.user
    if request.method=="GET":

        # 如果没有登陆的话就重定向到首页
        data = {
            "user": user.to_dict()
        }
        return render_template('news/user_base_info.html', data=data)

    # 2.如果不是就是post请求,代表是要修改用户数据
    # 取到传入的参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    # 判断获取的这些参数是否都有值
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 判断获取的gender参数是否在需要的值内
    if gender not in (['MAN', 'WOMAN']):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3. 更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将 session 中保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 4. 返回响应
    return jsonify(errno=RET.OK, errmsg="更新成功")



@profile_blu.route('/info')
@user_login_data
def user_info():
    """用户的个人信息页面渲染"""
    user=g.user

    # 如果没有登陆的话就重定向到首页
    if not user:
        return redirect("/")

    data={
        "user":user.to_dict()
    }
    return render_template('news/user.html',data=data)