from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
#from yourapplication.database import metadata, db_session
 
db = SQLAlchemy()

class Entry(db.Model):
  __tablename__ = 'entries'
  User_id = db.Column(db.Integer, primary_key = True)
  Username =db.Column(db.String(100))
  Name = db.Column(db.String(100))
  Email_id = db.Column(db.String(120), unique=True)
  Pwdhash = db.Column(db.String(54))
  Privilege = db.Column(db.Integer)
  Profile_pic = db.Column(db.LargeBinary)
  DOB = db.Column(db.Date)
  Last_login = db.Column(db.Date)



  def __init__(self, Username, Name, Email_id, Pwdhash, Privilege, Profile_pic, DOB, Last_login):
    def set_password( Pwdhash):
        self.pw_hash = generate_password_hash(Pwdhash)

    def check_password( Pwdhash):
        return check_password_hash(self.pw_hash, Pwdhash)

    self.Username = Username.title()
    self.Email_id = Email_id.lower()
    self.Pwdhash = set_password(Pwdhash)
    self.Name = Name
    self.Privilege = Privilege
    self.DOB = DOB
    self.Profile_pic = Profile_pic
    self.Last_login = Last_login

  