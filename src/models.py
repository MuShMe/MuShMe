import pymysql  
from helpers import *


conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='crimson', db='MuShMe', charset='utf8') 
database = conn.cursor()


#Function to check and add album data
def albumHook(albumname, art,albumartist, publisher, year):
   
  flag = 0
  foundalbums = database.execute("SELECT Album_id,Album_name FROM albums WHERE Album_name='%s'" % (albumname))
  results = database.fetchall()

  for result in results:
    foundbyartist = database.execute("SELECT Artist_name FROM artists WHERE Artist_id IN (SELECT Artist_id FROM album_artists WHERE Album_id='%s'" %
                                    (result)) 
    if foundbyartist > 0 :
      flag = 1

  if flag == 1:
    database.execute("INSERT INTO albums(Album_pic, Album_name, Publisher, Album_year) VALUES('%s','%s','%s',%s)" % 
                      (art,albumname, publisher, year))
    conn.commit()


#Function to check and add song data
def artistHook(albumartist):
  insert = database.execute
  pass


#Main insert function
def dbinsert(metadata):
  insert = database.execute
  commit = conn.commit

  insertvalues = {}

  for key in metadata:

    if key == 'title':
      insertvalues['Song_Title'] = metadata['title'][0]
    elif key == 'album':
      insertvalues['Song_Album'] = metadata['album'][0]
      albumHook(metadata['album'][0],'static/AlbumArt/'+ metadata['album'][0]+metadata['artist'][0]+'.png',
                metadata['artist'][0], publisherkey(metadata)[0],
                metadata['date'][0].rsplit('-',2)[0])

    elif key == 'artist':
      artistHook(metadata['artist'])
    elif key == 'copyright':
      insertvalues['Publisher'] = metadata['copyright'][0]
    elif key == 'publisher':
      insertvalues['Publisher'] = metadata['publisher'][0]
    elif key == 'genre':
      insertvalues['Genre'] = metadata['genre'][0]
  
  #insert this data into the main songs list
  if (database.execute("SELECT * from songs WHERE Song_Title='%s' AND Song_Album='%s'" 
                        % (metadata['title'][0], metadata['album'][0])) == 0):
    
    query = u'INSERT INTO songs('
    for key in insertvalues:
      query = unicode(query) + unicode(key) + u','
    
    query = unicode(query[:-1]) +u')'
    query += u' VALUES ('
    for key in insertvalues:
      query = unicode(query) + u"'"+unicode(insertvalues[key]) +u"'"+ u','
    query = unicode(query[:-1]) + u') '

    if insertvalues : 
      insert(query)
      commit()
      return True

  return False    