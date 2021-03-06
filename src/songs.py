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


def getLiked(songid):
  likes = g.database.execute("SELECT User_id FROM user_like_song WHERE User_id=%s AND Song_id=%s", (session['userid'],songid))

  if likes > 0:
    return True
  else:
    return False


def getplaylists():
  g.database.execute("SELECT Playlist_id FROM playlists WHERE User_id=%s" % (session['userid']))
  playlists = g.database.fetchall()
  retval = []

  for playlist in playlists:
    data = {}
    g.database.execute("SELECT Playlist_name FROM playlists WHERE Playlist_id=%s" % (playlist[0]))
    data['playname'] = g.database.fetchone()[0]
    data['playid'] = playlist[0]
    retval.append(data)

  return retval


def getArtistData(songid):
  data = {}
  g.database.execute("SELECT Artist_id FROM song_artists WHERE Song_id='%s'" % songid)
  artistids = g.database.fetchall()
  artist = []

  for artistid in artistids:
    g.database.execute("SELECT Artist_id,Artist_name, Artist_pic FROM artists WHERE Artist_id=%s" % artistid[0])
    temp = g.database.fetchone()

    if temp:
      data['id'] = temp[0]
      data['name'] = temp[1]
      data['pic'] = temp[2]

      if data['pic'] == None:
        data['pic'] = 'img/artist.jpg'
      artist.append(data)

  return artist


def getOthers(songid):
  others = []

  g.database.execute("SELECT Song_Album FROM songs WHERE Song_id=%s" % songid)
  album = g.database.fetchone()[0]
  g.database.execute("SELECT Song_id,Song_title FROM songs WHERE Song_Album='%s' LIMIT 5" % album)
  result = g.database.fetchall()

  for res in result:
    data = {}
    data['songid'] = res[0]
    data['title'] = res[1]
    others.append(data)

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


def getLikers(songid):
  g.database.execute("SELECT User_id FROM user_like_song WHERE Song_id=%s" % (songid))
  retval= []

  likers = g.database.fetchall()

  for liker in likers:
    data = {}
    data['userid'] = str(liker[0])
    g.database.execute("SELECT Username, Profile_pic FROM entries WHERE User_id=%s" % (liker[0]))
    userdata = g.database.fetchone()
    data['username'] = userdata[0]
    if userdata[1] != None:
      data['profilepic'] = userdata[1]
    else:
      data['profilepic'] = ""
    
    retval.append(data)

  return retval


def getFriendsToRecommend(songid):
  g.database.execute("SELECT User_id1 FROM friends WHERE User_id2=%s AND User_id1 NOT IN (SELECT User_id_to FROM recommend WHERE User_id_from=%s AND Recommend_id IN (SELECT Recommend_id FROM recommend_songs WHERE Song_id=%s))", (session['userid'], session['userid'], songid));
  friendset1= g.database.fetchall()
  g.database.execute("SELECT User_id2 FROM friends WHERE User_id1=%s AND User_id2 NOT IN (SELECT User_id_to FROM recommend WHERE User_id_from=%s AND Recommend_id IN (SELECT Recommend_id FROM recommend_songs WHERE Song_id=%s))", (session['userid'], session['userid'], songid));
  friendset2 = g.database.fetchall()
  retval = []

  for friend in friendset1:
    data = {}
    g.database.execute("SELECT Username,Profile_pic FROM entries WHERE User_id=%s", (friend[0]))
    userdata = g.database.fetchone()
    data['userid'] = friend[0]
    data['username'] = userdata[0]
    if userdata[1] != None:
      data['profilepic'] = userdata[1]
    else:
      data['profilepic'] = ""
    retval.append(data)

  for friend in friendset2:
    data = {}
    g.database.execute("SELECT Username,Profile_pic FROM entries WHERE User_id=%s", (friend[0]))
    userdata = g.database.fetchone()
    data['userid'] = friend[0]
    data['username'] = userdata[0]
    
    if userdata[1] != None:
      data['profilepic'] = userdata[1]
    else:
      data['profilepic'] = ""

    retval.append(data)

  return retval


@SONG.route('/song/<songid>')
def songPage(songid):
  if g.database.execute("SELECT * FROM songs WHERE Song_id=%s" % songid) == 0:
    if 'username' in session:
        abort(404)
    else:
      abort("You must be logged in to see this page.")
  
  return render_template('songpage/index.html', data=getSongData(songid),
              artists=getArtistData(songid), likes=getLikes(songid),
              likers = getLikers(songid), 
              others=getOthers(songid),
              commentform=CommentForm(),
              songid=songid,
              comments= getComments(songid),
              art=getAlbumArt(songid),
              form6 = searchForm(),
              reportform= ReportForm(),
              playlists=getplaylists(),
              friends=getFriendsToRecommend(songid),
              liked=getLiked(songid))


@SONG.route("/song/<int:songid>/<userid>/addtoplaylist", methods=["POST"])
def playlistAdd(songid, userid):
  playname = request.form['btn']

  query = ("""SELECT Playlist_id FROM playlists WHERE User_id=%s AND Playlist_name='%s' """ % 
                      (userid, playname))
  g.database.execute(query)

  playlistid = g.database.fetchone()

  if playlistid[0] != None:
    g.database.execute("""SELECT Song_id FROM song_playlist WHERE Playlist_id=%s""" % (playlistid[0]))
    presentsongids = g.database.fetchall()

    add=0

    for presentsongid in presentsongids:
      if songid == presentsongid[0]:
        add=1

    if add==0:
      query = ("INSERT INTO song_playlist(Song_id,Playlist_id) VALUES (%s,%s)" 
                          %(songid,playlistid[0]))

      g.database.execute(query)
      g.conn.commit()

  return redirect(url_for('SONG.songPage', songid=songid))


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


@SONG.route('/song/<songid>/like', methods=['POST'])
def user_like(songid):
  if request.form['liketype'] == "Like":
    query = (("SELECT * FROM user_like_song WHERE Song_id=%s AND User_id=%s") % (songid,session['userid']))

    if (g.database.execute(query) == 0):
      query = ("INSERT INTO user_like_song(Song_id, User_id) VALUES (%s,%s)" % (songid, session['userid']))
      print query
      g.database.execute(query)
      g.conn.commit()
  
  else:
    g.database.execute("DELETE FROM user_like_song WHERE Song_id=%s AND User_id=%s", (songid, session['userid']))
    g.conn.commit()

  return redirect(url_for('SONG.songPage', songid=songid))


@SONG.route('/song/<songid>/recommend/', methods=['POST'])
def recommendSong(songid):
  print request.form
  for name in request.form:
  
    if request.form[name] == "Recommend":
  
      g.database.execute("SELECT max(Recommend_id) FROM recommend");
      recommendid = g.database.fetchone()

      if recommendid[0] == None:
        recommendid = 1
      else:
        recommendid = recommendid[0] + 1

      print recommendid, session['userid'], name
      query = ("INSERT INTO recommend VALUES(%s,%s,%s,CURDATE())" % (recommendid,session['userid'],name))
      g.database.execute(query);
      g.conn.commit()

      query = ("INSERT INTO recommend_songs(Song_id, Recommend_id) VALUES (%s,%s)" % (songid, recommendid))
      g.database.execute(query);
      g.conn.commit()


  return redirect(url_for('SONG.songPage', songid=songid))