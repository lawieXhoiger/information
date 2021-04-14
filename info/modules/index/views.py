from info import redis_store
from . import index_blu


@index_blu.route("/")
def index():
    # redis_store.set('name','itcast')
    redis_store.set('name','itheima')
    # 向redis中取一个值
    return 'index'
