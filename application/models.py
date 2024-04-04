from .database import db 
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    userIdNo = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True, unique=True)
    userId = db.Column(db.String, unique=True, nullable=False)
    companyName = db.Column(db.String,)
    userPassword = db.Column(db.String, nullable=False)
    dataFolder = db.Column(db.String, nullable=False, unique = True)
    portNo = db.Column(db.Integer)
    countOfModels = db.Column(db.Integer, default = 0)
    def get_id(self):
        return self.userIdNo

class FilesUploaded(db.Model):
    __tablename__ = 'FilesUploaded'
    fileId = db.Column(db.Integer, nullable=False, primary_key=True)
    fileName = db.Column(db.String, nullable=False)
    fileOwner = db.Column(db.String, db.ForeignKey('users.userId') , nullable=False)

