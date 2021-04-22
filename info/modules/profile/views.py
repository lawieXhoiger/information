from flask import current_app
from flask import g, jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from info import db
from info.modules.profile import profile_blu
from info.utils.common import user_login_data
from info.utils.response_code import RET


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
    user=g.user

    # 如果没有登陆的话就重定向到首页
    if not user:
        return redirect("/")

    data={
        "user":user.to_dict()
    }
    return render_template('news/user.html',data=data)