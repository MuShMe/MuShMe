from flask import Blueprint, render_template, request, redirect, url_for
from flask import g, abort
from flask import session
from Forms import CommentForm

artist = Blueprint('SONG',__name__,template_folder='templates')


def getArtistata(artistid):
  data = {}
  g.database.execute("SELECT Artist_name, Begin_date_year, End_date_year, Last_updated FROM artists WHERE Artist_id= %s" % artistid)
  row = g.database.fetchall()[0]

  data['artist_name'] = row[0]
  g.database.execute("SELECT Album_id from albums_artists ORDER BY added_on LIMIT 1")
  data['Album_id']=g.database.fetchone()[0]
  data['Begin_date_year'] = row[1]
  data['End_date_year'] = row[2]
  data['Last_updated'] = row[3]
  return data

def getLikes(artistid):
  g.database.execute("SELECT count(*) FROM user_like_song where Song_id='%s'" % songid)
  return g.database.fetchone()[0]


def getArtistData(artistid):
  data = {}
  g.database.execute("SELECT Artist_id FROM song_artists WHERE Song_id='%s'" % songid)
  artistids = g.database.fetchall()
  artist = []

  for artistid in artistids:
    g.database.execute("SELECT Artist_id,Artist_name FROM artists WHERE Artist_id=%s" % artistid[0])
    temp = g.database.fetchone()

    if temp:
      data['id'] = temp[0]
      data['name'] = temp[1]
      print data
      artist.append(data)

  return artist


def getOthers(artistid):
  others = []

  g.database.execute("SELECT Song_Album FROM songs WHERE Song_id=%s" % songid)
  album = g.database.fetchone()[0]
  g.database.execute("SELECT Song_title FROM songs WHERE Song_Album='%s' LIMIT 5" % album)
  result = g.database.fetchall()

  for res in result:
    others.append(res[0])

  return others

def getAlbumArt(artistid):
  g.database.execute("SELECT Song_Album FROM songs WHERE song_id=%s", (songid))
  albumname = g.database.fetchone()[0]

  g.database.execute("SELECT Album_pic FROM albums WHERE Album_id=%s", (albumname))
  return g.database.fetchone()[0]

@SONG.route('/song/<artistid>')
def songPage(artistid):
  if g.database.execute("SELECT * FROM artists WHERE Artist_id=%s" % artistid) == 0:
    if 'username' in session:
        abort(404)
    else:
      abort("You must be logged in to see this page.")
  
  return render_template('songpage/index.html', data=getSongData(songid),
              artists=getArtistData(songid), likes=getLikes(songid), 
              others=getOthers(songid),
              commentform=CommentForm(),
              songid=songid,
              comments= getComments(songid),
              art=getAlbumArt(songid))
