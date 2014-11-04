from flask import Blueprint, render_template
from flask import g

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
  g.database.execute("SELECT Artist_id FROM song_artists WHERE Song_id='%s'" % songid)
  artistids = g.database.fetchall()
  
  artist = []

  for artistid in artistids:
  	g.database.execute("SELECT Aritst_name FROM artists WHERE Artist_id=%s" % artistid)
  	artist.append(g.database.fetchone()[0])
  
  return artist


@SONG.route('/song/<songid>')
def songPage(songid):
    return render_template('songpage/index.html', data=getSongData(songid),
                            artists=getArtistData(songid), likes=getLikes(songid))