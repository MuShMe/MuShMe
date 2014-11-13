# @Author rootavish, copyright the DBMS team 2014
# API for the MuShMe service.
from flask import Blueprint
from flask import Flask, request, g
from models import dbinsert
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from src import app
import json


API = Blueprint('API',__name__,template_folder='templates')

def addtodatabase(metadata):
    if (dbinsert(metadata, imagefilename) == True):
        return True
    else:
        return False


#function to add the data from the request json to the database:
@API.route('/api/addtocollection',methods=['POST'])
def getjson():

    if verify_auth_token(request.json['token']) == False:
          return "Authentication failure"

    if addtodatabase(request.json) == True:
        return "Successfully added "+request.json['title'][0] + " by " + request.json['artist'][0] + " to your collection."    
    else:
        return "Could not add this song to the database, make sure the tags for the song are complete."


@API.route('/api/auth/', methods=['POST'])
def getKey():
    email = request.json['email']
    password = request.json['password']
    query = ("""SELECT User_id, Pwdhash FROM entries WHERE Email_id='%s' """ % (email))
    g.database.execute(query)
    result = g.database.fetchone()

    response = {}

    if result == None:
        response['invalid'] = "Invalid username or password"
        return json.dumps(response)

    if password == result[1]:
         response['token'] = generate_auth_token(result[0])
         response['userid'] = result[0]
    else:
        response['invalid'] = "Authentication failure"

    responsejson= json.dumps(response)
    return responsejson


def generate_auth_token(userid, expiration = 1000):
    s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
    return s.dumps({ 'id': userid })


def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return False # valid token, but expired
    except BadSignature:
        return False # invalid token
    return True