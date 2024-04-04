from flask import Flask 
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_bcrypt import Bcrypt
app = None
def createApp():
    app = Flask(__name__, template_folder="templates")
    app.app_context().push()
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    print("Creating app")
    return app

app = createApp()

bcrypt = Bcrypt(app)

from application.controllers import *

# @app.route('/')
# def home():
#     print("hello world")
#     return "hello world"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)