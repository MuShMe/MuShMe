from models import database, conn
from flask import Blueprint, render_template

SONG = Blueprint('SONG',__name__,template_folder='templates')


def getSongData(songid):
  data = {}
  database.execute("SELECT Song_title, Song_Album, Genre, Publisher FROM songs WHERE Song_id= %s" % songid)
  row = database.fetchall()[0]

  data['song_name'] = row[0]
  data['song_album'] = row[1]
  data['genre'] = row[2]
  data['publisher'] = row[3]
  
  return data

def getLikes(songid):
  database.execute("SELECT count(*) FROM user_like_song where Song_id='%s'" % songid)
  return database.fetchone()[0]


def getArtistData(songid):
  database.execute("SELECT Artist_id FROM song_artists WHERE Song_id='%s'" % songid)
  artistids = database.fetchall()
  
  artist = []

  for artistid in artistids:
  	database.execute("SELECT Aritst_name FROM artists WHERE Artist_id=%s" % artistid)
  	artist.append(database.fetchone()[0])
  
  return artist


@SONG.route('/song/<songid>')
def songPage(songid):
    return render_template('songpage/index.html', data=getSongData(songid),
                            artistdata=getArtistData(songid), likes=getLikes(songid))