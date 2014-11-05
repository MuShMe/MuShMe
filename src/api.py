# @Author rootavish, copyright the DBMS team 2014
# API for the MuShMe service.
from flask import Blueprint
from flask import Flask, request
from models import dbinsert

#To recieve images
import base64

API = Blueprint('API',__name__,template_folder='templates')

def addtodatabase(metadata):
    imagefilename = metadata['artist'][0] + metadata['album'][0] + '.png'

    if (dbinsert(metadata, imagefilename) == True):
        return True
    else:
        return False
    
#function to add the data from the request json to the database:
@API.route('/api/addtocollection',methods=['GET','POST'])
def getjson():
    
    if addtodatabase(request.json) == True:
        return "Successfully added "+request.json['title'][0] + " by " + request.json['artist'][0] + " to your collection."
    
    else:
        return "Could not add this song to the database, make sure the tags for the song are complete."