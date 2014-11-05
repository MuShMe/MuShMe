from flask import Blueprint, render_template
from flask import g, abort
from flask import session

SONG = Blueprint('SONG',__name__,template_folder='templates')


def getSongData(songid):
  data = {}
  g.database.execute("SELECT Song_title, Song_Album, Genre, Publisher, Song_year FROM songs WHERE Song_id= %s" % songid)
  row = g.database.fetchall()[0]

  data['song_name'] = row[0]
  data['song_album'] = row[1]
  data['genre'] = row[2]
  data['publisher'] = row[3]
  data['year'] = row[4]
  return data

def getLikes(songid):
  g.database.execute("SELECT count(*) FROM user_like_song where Song_id='%s'" % songid)
  return g.database.fetchone()[0]


def getArtistData(songid):
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

def getOthers(songid):
  others = []

  g.database.execute("SELECT Song_Album FROM songs WHERE Song_id=%s" % songid)
  album = g.database.fetchone()[0]
  g.database.execute("SELECT Song_title FROM songs WHERE Song_Album='%s' LIMIT 5" % album)
  result = g.database.fetchall()

  for res in result:
    others.append(res[0])

  return others


@SONG.route('/song/<songid>')
def songPage(songid):
  if g.database.execute("SELECT * FROM songs WHERE Song_id=%s" % songid) == 0:
    if 'username' in session:
        abort(404)
    else:
      abort("You must be logged in to see this page.")
  
  return render_template('songpage/index.html', data=getSongData(songid),
              artists=getArtistData(songid), likes=getLikes(songid), 
              others=getOthers(songid))