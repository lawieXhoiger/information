from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

class Config(object):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI="mysql://root:mysql@127.0.0.1:3306/information27"
    SQLALCHEMY_TRACK_MODIFICATIONS=False


app = Flask(__name__)
# 加载配置
app.config.from_object(Config)


db=SQLAlchemy(app)

@app.route("/")
def index():
    return '22222+see world'


if __name__ == "__main__":
     app.run()
