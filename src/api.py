# @Author rootavish, copyright the DBMS team 2014
# API for the MuShMe service.
from flask import Blueprint
from flask import Flask, request

API = Blueprint('API',__name__,template_folder='templates')

def addtodatabase(metadata):
	print metadata
	
	return True

#function to add the data from the request json to the database:
@API.route('/api/addtocollection',methods=['GET','POST'])
def getjson():
    
    if addtodatabase(request.json) == True:
    	return "Successfully added "+request.json['TITLE']+" by "+request.json['ARTIST'] + " to your collection."
    
    else:
    	return "Could not add this song to the database, make sure the tags for the song are complete."

