from flask import current_app
from flask import render_template

from info import redis_store
from . import index_blu


@index_blu.route("/")
def index():
    # # redis_store.set('name','itcast')
    # redis_store.set('name','itheima')
    # # 向redis中取一个值
    # return 'index'
    return render_template('news/index.html')

# 打开网页时候，浏览器会默认取请求根路径+/favicon.ico做网站标签的小图标
# send_static_file是flask去查指定的文件调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')