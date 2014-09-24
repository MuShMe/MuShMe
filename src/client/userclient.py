#This is a client to read data from ID3 tags and POST the data to the mushme database

import os
import sys

#For the network capabilities
import urllib2
import urllib

#For parsing the ID3 tags
import ID3

def read(library):
    
    if library[-1] != '/':
        library += '/'

    for file in os.listdir(library):

        if os.path.isdir(library + file) == False:
            #send data from file to server as a JSON


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
