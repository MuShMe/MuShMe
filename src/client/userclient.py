# This is a client to readtags data from ID3 tags and POST the data to the mushme database
# @Author rootavish, copyright the DBMS team, 2014

import os
import sys

#To create a json to throw at the server
import json
#To encode the image into the json
import base64

#For the network capabilities
import urllib2
import urllib

#For parsing the ID3 tags
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen import File

#for reading passwords
import getpass
#For hashing said passwords
import hashlib

def readtags(library, authreturn, headers):
    
    if library[-1] != '/':
        library += '/'

    for files in os.listdir(library):

        filepath=library + files
        #print filepath

        if os.path.isdir(filepath) == False:
            ext= os.path.splitext(filepath)[-1].lower() 
            
            #print ext

            if ext == ".mp3":

                filename = File(library+files)
                id3tags = dict(MP3(library+files, ID3= EasyID3))

                if 'APIC:' in filename.tags and 'artist' in id3tags and 'album' in id3tags: 
                    id3tags['ART'] = base64.b64encode(filename.tags['APIC:'].data)
                    id3tags['token']= authreturn['token']
                    id3tags['userid'] = authreturn['userid']
                    
                    if 'title' in id3tags and 'artist' in id3tags and 'album' in id3tags:
                    #encode the tags into a JSON to send to the server
                        tagjson = json.dumps(id3tags)

                        request = urllib2.Request('http://localhost:5000/api/addtocollection',tagjson, headers)
                        response = urllib2.urlopen(request)
                        print str(response.read())
                        
                        if (str(response.read()) == 'Authentication failure'):
                            sys.exit(0)

                    else:
                        print("Tags for %s are not complete, not added to database, or collection.", library+ files)        
        else:
            readtags(filepath, authreturn, headers)


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
        #Authenticate the user
        auth = {}
        headers = {}
        headers['Content-Type'] = 'application/json'

        auth['email'] = raw_input("Enter email-id for mushme.com: ")
        auth['password'] = hashlib.sha1(getpass.getpass("Enter password for %s: " % auth['email'])).hexdigest()

        request = urllib2.Request('http://localhost:5000/api/auth/',json.dumps(auth), headers)
        response = urllib2.urlopen(request)

        authreturn = json.load(response)

        if 'token' not in authreturn:
            print("Authentication failure.")
            sys.exit(0)

        readtags(library,authreturn,headers)
    else:
        print(library + ' is not a valid path to a folder')
        sys.exit(2)

if __name__=="__main__":
    main()
