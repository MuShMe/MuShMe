from flask import Blueprint, render_template, request, redirect, url_for
from flask import g, abort
from flask import session
from Forms import CommentForm
from Forms import searchForm, ReportForm

SONG = Blueprint('SONG',__name__,template_folder='templates')


def getSongData(songid):
  data = {}
  g.database.execute("SELECT Song_title, Song_Album, Genre, Publisher, Song_year FROM songs WHERE Song_id= %s" % songid)
  row = g.database.fetchall()[0]

  data['song_name'] = row[0]
  g.database.execute("SELECT Album_name from albums WHERE Album_id=%s", (row[1]))
  data['song_album'] = g.database.fetchone()[0]
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

def getComments(songid):
  g.database.execute("SELECT Comment_id from song_comments WHERE Song_id=%s  ORDER BY Comment_id DESC", (songid))
  comments = g.database.fetchall()

  commentlist = []

  for comment in comments:
    data = {}
    g.database.execute("SELECT User_id, Comment FROM comments WHERE Comment_id=%s", (comment[0]))
    row = g.database.fetchone()
    data['commentid'] = comment[0]
    data['userid'] = row[0]
    data['comment_text'] = row[1]

    g.database.execute("SELECT Username FROM entries WHERE User_id=%s", (row[0]))
    data['username'] = g.database.fetchone()[0]
    commentlist.append(data)

  return commentlist


def getAlbumArt(songid):
  g.database.execute("SELECT Song_Album FROM songs WHERE song_id=%s", (songid))
  albumname = g.database.fetchone()[0]

  g.database.execute("SELECT Album_pic FROM albums WHERE Album_id=%s", (albumname))
  return g.database.fetchone()[0]

@SONG.route('/song/<songid>')
def songPage(songid):
  if g.database.execute("SELECT * FROM songs WHERE Song_id=%s" % songid) == 0:
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
              art=getAlbumArt(songid),
              form6 = searchForm(),
              reportform= ReportForm())

@SONG.route("/song/<userid>/addtoplaylist")
def playlistAdd(userid):
  pass


@SONG.route('/song/addcomment/<int:songid>', methods=["POST"])
def addcomment(songid):
  g.database.execute("SELECT max(Comment_id) FROM comments")
  pk = g.database.fetchone()[0]

  if pk == None:
    pk = 1
  else:
    pk = pk + 1

  comment_type = "S"
  g.database.execute("""INSERT INTO comments VALUES (%s, "%s", "%s",%s, %s)""", (pk,comment_type, request.form['comment'],'0', session['userid']))
  g.conn.commit()
  g.database.execute("""INSERT INTO song_comments VALUES (%s,%s)""", (songid,pk))
  g.conn.commit()
  return redirect(url_for('.songPage', songid=songid))


@SONG.route('/song/report/<songid>/<commentid>/', methods=['POST'])
def reportsongcomment(songid,commentid):
    query = ("""INSERT INTO complaints(Complain_type, Complain_description, Comment_id, reported_by) VALUES ("%s", "%s", %s, %s)
        """ % (request.form['report'], request.form['other'], commentid, session['userid']))
    g.database.execute(query)
    g.conn.commit()
    return redirect(url_for('SONG.songPage', songid=songid))
