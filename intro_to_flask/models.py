from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
#from yourapplication.database import metadata, db_session
 
db = SQLAlchemy()

class Entry(db.Model):
  __tablename__ = 'entries'
  uid = db.Column(db.Integer, primary_key = True)
  username =db.Column(db.String(100))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(54))
   
  def __init__(self, username, email, password):
    self.username = username.title()
    self.email = email.lower()
    self.set_password(password)
    
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
 
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)