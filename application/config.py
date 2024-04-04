import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG= False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR,"AVABOT_DB.sqlite3")
    SECRET_KEY = 'SHAURYA Loves HULK'
