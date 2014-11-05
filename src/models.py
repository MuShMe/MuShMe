import pymysql  
from helpers import *
from flask import g


#Function to check and add album data
def albumHook(albumname, art,albumartist, publisher, year):
  flag = 0
  foundalbums = g.database.execute("SELECT Album_id FROM albums WHERE Album_name='%s'" % (albumname))
  results = g.database.fetchall()

  for result in results:
    foundbyartist = g.database.execute("SELECT Artist_name FROM artists WHERE Artist_id IN (SELECT Artist_id FROM album_artists WHERE Album_id='%s')" %
                                      (result[0]))
    if foundbyartist > 0 :
      flag = 1

  if flag == 0:
    g.database.execute("INSERT INTO albums(Album_pic, Album_name, Publisher, Album_year) VALUES('%s','%s','%s',%s)" % 
                      (art,albumname, publisher, year))
    g.conn.commit()
  
  g.database.execute("SELECT Album_id FROM albums WHERE Album_name='%s' AND Album_pic='%s'" % (albumname, art))
  a= g.database.fetchone()[0]
  return a


#Function to check and add artist data
def artistHook(artistnames, albumname,albumid, date):
  #Check if the artist exists already.
  for artistname in artistnames:
    artistexists = g.database.execute("SELECT * FROM artists WHERE Artist_name='%s'" % artistname)

    if artistexists == False:
      g.database.execute("INSERT INTO artists(Artist_name, Last_updated) VALUES('%s','%s')" % (artistname, date))
      g.conn.commit()

      g.database.execute("SELECT Artist_id FROM artists WHERE Artist_name='%s' AND Last_updated='%s'" % (artistname, date))
      artistid= g.database.fetchone()[0]
      g.database.execute("INESRT INTO album_artists VALUES (%s, %s)" % (artistid, albumid))
    else:
      g.database.execute("SELECT Artist_id FROM artists WHERE Artist_name='%s' AND Last_updated='%s'" % (artistname, date))
      artistid= g.database.fetchone()[0]

      found = g.database.execute("SELECT * FROM album_artists WHERE Artist_id=%s AND Album_id=%s" % (artistid, albumid))
      if found == 0:
        g.database.execute("INSERT INTO album_artists(Artist_id, Album_id) VALUES (%s,%s)" % (artistid, albumid));
        g.conn.commit()

      return artistid


#Main insert function
def dbinsert(metadata, imagefilename):
  insert = g.database.execute
  commit = g.conn.commit

  insertvalues = {}

  for key in metadata:

    if key == 'title':
      insertvalues['Song_Title'] = metadata['title'][0]
    elif key == 'album':
      insertvalues['Song_Album'] = metadata['album'][0]
      albumid = albumHook(metadata['album'][0],'AlbumArt/'+ metadata['artist'][0]+metadata['album'][0]+'.png',
                          metadata['artist'][0], publisherkey(metadata)[0],
                          metadata['date'][0].rsplit('-',2)[0])
    
    elif key == 'artist':
      artistid = artistHook(metadata['artist'], metadata['album'][0],albumid, metadata['date'][0].split()[0])
    elif key == 'copyright':
      insertvalues['Publisher'] = metadata['copyright'][0]
    elif key == 'publisher':
      insertvalues['Publisher'] = metadata['publisher'][0]
    elif key == 'genre':
      insertvalues['Genre'] = metadata['genre'][0]
    elif key == 'date':
      insertvalues['Song_year'] = metadata['date'][0].rsplit('-',2)[0]

  #insert this data into the main songs list
  if (g.database.execute("SELECT * from songs WHERE Song_Title='%s' AND Song_Album='%s'" 
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
      g.database.execute("SELECT Song_id FROM songs WHERE Song_Title='%s' AND Song_Album='%s'"
                         % (metadata['title'][0], metadata['album'][0]))
      songid = g.database.fetchone()[0]

      g.database.execute("INSERT INTO song_artists VALUES (%s,%s)" % (songid, artistid))
      commit()
      return True

  return False    