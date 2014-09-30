#This is a client to read data from ID3 tags and POST the data to the mushme database

import os
import sys

#To create a json to throw at the server
import json

#For the network capabilities
import urllib2
import urllib

#For parsing the ID3 tags
from ID3 import *

def read(library):
    
    if library[-1] != '/':
        library += '/'

    for files in os.listdir(library):

        filepath=library + files
        #print filepath

        if os.path.isdir(filepath) == False:
            ext= os.path.splitext(filepath)[-1].lower() 
            #print ext

            if ext == ".mp3":

                id3tags=ID3(library+files);
                #encode the tags into a JSON to send to the server
                tagjson=json.dumps(id3tags.as_dict()).encode('utf-8')

                headers = {}
                headers['Content-Type'] = 'application/json'
                request = urllib2.Request('http://localhost:5000/api/addtocollection/1',tagjson, headers)
                response = urllib2.urlopen(request)
                print str(response.read())

'''
MAIN starts here
'''
def main():
    arguments = len(sys.argv)

    if arguments < 2:
        print("Usage: scrobbleme [path to library]")
        sys.exit(1)
    else:
        library = sys.argv[1]

    if os.path.isdir(library):
        read(library)
    else:
        print(library + ' is not a valid path to a folder')
        sys.exit(2)

if __name__=="__main__":
    main()
