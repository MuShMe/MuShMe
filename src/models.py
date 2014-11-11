import pymysql  
from helpers import *
from flask import g
#To add images.
import base64

#insert references for this shiz into the user's default playlist.
def GetPlaylistID(userid):
  g.database.execute("""SELECT Username FROM entries WHERE User_id=%s""", (userid))
  
  playlistname= g.database.fetchone()[0]
  
  playlistname += " default collection"

  query = ("""SELECT Playlist_id FROM playlists WHERE User_id=%s AND Playlist_name='%s'""" %
                    (userid, playlistname))
  g.database.execute(query)
    
  return g.database.fetchone()[0]


#To insert a song into the user's playlist
def playlistInsert(songid, playlistid):
  found = g.database.execute("""SELECT * FROM song_playlist WHERE Song_id=%s AND Playlist_id=%s""" % (songid, playlistid))
  
  if found == 0:  
    g.database.execute("""INSERT INTO song_playlist VALUES (%s ,%s)"""% (songid, playlistid))
    g.conn.commit()



def artistalbum(albumid, artistids):
  for artistid in artistids:
    query = ("SELECT * FROM album_artists WHERE Artist_id=%s AND Album_id=%s" % (artistid, albumid[0]))
    present = g.database.execute(query)

    if not present:
      query = ("INSERT INTO album_artists(Album_id,Artist_id) VALUES (%s,%s)"% (albumid[0],artistid))
      g.database.execute(query)
      g.conn.commit()


#function to check and add album data
def albumHook(albumname, imagefilename, artdata, albumartist, publisher, year):
  g.database.execute("""SELECT Album_id FROM albums WHERE Album_name='%s'""" % (albumname))

  albums = g.database.fetchall()

  for album in albums:

    g.database.execute("""SELECT Artist_id FROM album_artists WHERE Album_id=%s""", album[0])

    artists = g.database.fetchall()

    for artist in artists:
      g.database.execute("""SELECT Artist_name FROM artists WHERE Artist_id=%s""" % artist[0])

      artistname = g.database.fetchone()

      if artistname[0] == albumartist:
        return album

#We didn't find anything. Make an entry and return the albumid.
  g.database.execute("SELECT max(Album_id) FROM albums");
  albumid = g.database.fetchone()
 
  if albumid[0] == None:
    albumid = 0
  else:
    albumid = albumid[0] + 1

  query = (u"""INSERT INTO albums(Album_id,Album_pic,Album_name,Album_year, Publisher) VALUES(%s, '%s','%s',%s,'%s')""" % (albumid, unicode(imagefilename), unicode(albumname), year, unicode(publisher)))

  g.database.execute(query)
  g.conn.commit()
  with open('src/static/'+imagefilename, 'wb') as f:
    f.write(base64.b64decode(artdata))

  array = []
  array.append(albumid)
  return array


#Function to check and add artist data
def artistHook(artistnames, date):
  
  retval = []
  
  #Check if the artist exists already.
  for artistname in artistnames:
    g.database.execute("SELECT Artist_id FROM artists WHERE Artist_name='%s'" % artistname)

    artistid = g.database.fetchone()

    if artistid == None:
      g.database.execute("""SELECT max(Artist_id) FROM artists""")
      Maxid = g.database.fetchone()

      if Maxid[0] == None:
        Maxid = 0
      else:
        Maxid = Maxid[0] + 1
      query = ("INSERT INTO artists(Artist_id, Artist_name, Last_updated) VALUES (%s,'%s','%s')"% (Maxid, artistname, date))
      g.database.execute(query)
      g.conn.commit()
      retval.append(Maxid)
    
    else:
      retval.append(artistid[0])

  return retval


#Main insert function
def dbinsert(metadata, imagefilename):
  insert = g.database.execute
  commit = g.conn.commit

  #Values to insert into the database.
  insertvalues = {}
  for key in metadata:
    if key == 'title':
      insertvalues['Song_Title'] = metadata['title'][0]
    elif key == 'album':
      albumid = albumHook(metadata['album'][0],
                          'AlbumArt/'+ imagefilename,
                          metadata['ART'],
                          metadata['artist'][0],
                           publisherkey(metadata)[0],
                          metadata['date'][0].rsplit('-',2)[0])
      insertvalues['Song_Album'] = albumid[0]

    elif key == 'artist':
      artistids = artistHook(metadata['artist'], metadata['date'][0].split()[0])
    elif key == 'copyright':
      insertvalues['Publisher'] = metadata['copyright'][0]
    elif key == 'publisher':
      insertvalues['Publisher'] = metadata['publisher'][0]
    elif key == 'genre':
      insertvalues['Genre'] = metadata['genre'][0]
    elif key == 'date':
      insertvalues['Song_year'] = metadata['date'][0].rsplit('-',2)[0]

  #Form artist album relationship
  artistalbum(albumid,artistids)

  #insert this data into the main songs list
  g.database.execute("SELECT Song_id from songs WHERE Song_Title='%s' AND Song_Album='%s'" 
                        % (metadata['title'][0], albumid[0]))
  songid = g.database.fetchone()
  playlistid = GetPlaylistID(metadata['userid'])

  if (songid == None):
    #First enter the song into the main songs table in the database.
    if insertvalues:
      
      query = u'INSERT INTO songs('
      
      for key in insertvalues:
        query = unicode(query) + unicode(key) + u','
      
      query = unicode(query[:-1]) +u')'
      query += u' VALUES ('
      
      for key in insertvalues:
        query = unicode(query) + u"'"+unicode(insertvalues[key]) +u"'"+ u','
      
      query = unicode(query[:-1]) + u') '
      print query
      insert(query)
      g.database.execute("SELECT Song_id FROM songs WHERE Song_Title='%s' AND Song_Album='%s'"
                         % (metadata['title'][0], albumid[0]))
      
      songid = g.database.fetchone()[0]
      playlistInsert(songid,playlistid)

      for artistid in artistids:
        g.database.execute("INSERT INTO song_artists VALUES (%s,%s)" % (songid, artistid))
      commit()
      return True
    else:
      return False    

  #if song exists, add it to only the playlist.
  else:
    playlistInsert(songid[0],playlistid)
    return True