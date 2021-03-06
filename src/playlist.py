from flask import Blueprint
from flask import g, redirect, render_template, request, session, url_for
from Forms import CommentForm, searchForm, ReportForm

playlist = Blueprint('playlist',__name__,template_folder='templates')


def getPlaylistName(playlistid):
    g.database.execute("""SELECT Playlist_name FROM playlists WHERE Playlist_id=%s""", (playlistid))
    playlistname= g.database.fetchone()

    if playlistname[0] == None:
        return ""
    else:
        return playlistname[0]


def getUserData(playlistid):
    g.database.execute("""SELECT User_id FROM playlists WHERE Playlist_id=%s""", (playlistid))
    userid = g.database.fetchone()[0]
    g.database.execute("""SELECT Username FROM entries WHERE User_id=%s""", (userid))
    username = g.database.fetchone()[0]
    data = {}
    
    data['userid'] = userid
    data['username'] = username

    return data


def getLikes(playlistid):
  g.database.execute("""SELECT count(*) FROM user_like_playlist WHERE Playlist_id=%s""", (playlistid))
  likes = g.database.fetchone()
  if likes[0]==None:
    return 0
  else:
    return likes[0]


def getLiked(playlistid):
  likes = g.database.execute("SELECT User_id FROM user_like_playlist WHERE User_id=%s AND Playlist_id=%s", (session['userid'],playlistid))

  if likes > 0:
    return True
  else:
    return False


def getLikers(playlistid):
  g.database.execute("SELECT User_id FROM user_like_playlist WHERE playlist_id=%s" % (playlistid))
  retval= []

  likers = g.database.fetchall()

  for liker in likers:
    data = {}
    data['userid'] = liker[0]
    g.database.execute("SELECT Username, Profile_pic FROM entries WHERE User_id=%s" % (liker[0]))
    userdata = g.database.fetchone()
    data['username'] = userdata[0]
    
    if (userdata[1] == None):
        data['profilepic'] = ""
    else:
        data['profilepic'] = userdata[1]
    
    retval.append(data)

  return retval


def getComments(playlistid):
    g.database.execute("SELECT Comment_id FROM playlist_comments WHERE Playlist_id=%s ORDER BY Comment_id DESC" % (playlistid))
    commentids = g.database.fetchall()
    retval = []

    for commentid in commentids:
        g.database.execute("SELECT Comment, User_id FROM comments WHERE Comment_id=%s", (commentid[0]))
        commentdata = g.database.fetchone()

        data = {}
        data['comment'] = commentdata[0]
        data['userid'] = commentdata[1]
        data['commentid'] = commentid[0]
        g.database.execute("SELECT Username FROM entries WHERE User_id=%s", (data['userid']))
        data['username'] = g.database.fetchone()[0]
        retval.append(data)

    return retval


def getPlaylistSongs(playlistid):
    g.database.execute("SELECT Song_id from song_playlist WHERE Playlist_id=%s", (playlistid))
    songs = g.database.fetchall()

    retval = []

    for song in songs:
        g.database.execute("SELECT Song_title,Song_Album FROM songs WHERE Song_id=%s", (song[0]))
        songdata = g.database.fetchone()
        
        data = {}
        data['songname'] = songdata[0]
        data['songid'] = song[0]
        g.database.execute("SELECT Album_pic FROM albums WHERE Album_id=%s", (songdata[1]))
        data['albumart'] = g.database.fetchone()[0]
        retval.append(data)

    return retval


def getFriendsToRecommend(playlistid):
  g.database.execute("SELECT User_id1 FROM friends WHERE User_id2=%s AND User_id1 NOT IN (SELECT User_id_to FROM recommend WHERE User_id_from=%s AND Recommend_id IN (SELECT Recommend_id FROM recommend_playlists WHERE Playlist_id=%s))", (session['userid'], session['userid'], playlistid));
  friendset1= g.database.fetchall()
  g.database.execute("SELECT User_id2 FROM friends WHERE User_id1=%s AND User_id2 NOT IN (SELECT User_id_to FROM recommend WHERE User_id_from=%s AND Recommend_id IN (SELECT Recommend_id FROM recommend_playlists WHERE Playlist_id=%s))", (session['userid'], session['userid'], playlistid));
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


@playlist.route('/playlist/report/<playlistid>/<commentid>/', methods=['POST'])
def reportcomment(playlistid,commentid):
    query = ("""INSERT INTO complaints(Complain_type, Complain_description, Comment_id, reported_by) VALUES ("%s", "%s", %s, %s)
        """ % (request.form['report'], request.form['other'], commentid, session['userid']))
    g.database.execute(query)
    g.conn.commit()
    return redirect(url_for('playlist.playlistPage', playlistid=playlistid))


@playlist.route('/playlist/<playlistid>/addcomment/', methods=['POST'])
def addcommentplaylist(playlistid):
    g.database.execute("SELECT max(Comment_id) FROM comments")
    pk = g.database.fetchone()[0]

    if pk == None:
        pk = 1
    else:
        pk = pk + 1

    comment_type = 'P'
    g.database.execute("""INSERT INTO comments VALUES (%s, "%s", "%s",%s, %s)""", (pk,comment_type, request.form['comment'],'0', session['userid']))
    g.conn.commit()
    g.database.execute("""INSERT INTO playlist_comments VALUES (%s,%s)""", (playlistid,pk))
    g.conn.commit()
    return redirect(url_for('playlist.playlistPage', playlistid=playlistid))


@playlist.route('/playlist/<playlistid>')
def playlistPage(playlistid):
    return render_template('playlist/index.html',
                            playlistid=playlistid, 
                            pname=getPlaylistName(playlistid), 
                            puserdata=getUserData(playlistid),
                            likes = getLikes(playlistid),
                            commentform= CommentForm(),
                            reportform= ReportForm(),
                            songs = getPlaylistSongs(playlistid),
                            Comments=getComments(playlistid),
                            form6= searchForm(),
                            likers= getLikers(playlistid),
                            friends=getFriendsToRecommend(playlistid),
                            liked=getLiked(playlistid))


@playlist.route('/playlist/<playlistid>/like', methods=['POST'])
def user_like(playlistid):
  
  if request.form['liketype'] == "Like":
    query = (("SELECT * FROM user_like_playlist WHERE Playlist_id=%s AND User_id=%s") % (playlistid,session['userid']))

    if (g.database.execute(query) == 0):
      query = ("INSERT INTO user_like_playlist(Playlist_id,User_id) VALUES (%s,%s)" % (playlistid, session['userid']))
      g.database.execute(query)
      g.conn.commit()
  
  else:
    g.database.execute("DELETE FROM user_like_playlist WHERE Playlist_id=%s AND User_id=%s", (playlistid, session['userid']))
    g.conn.commit()
  
  return redirect(url_for('playlist.playlistPage', playlistid=playlistid))


@playlist.route("/playlist/<playlistid>/deletesongs", methods=["POST"])
def deletesongs(playlistid):
    songlist =request.form.getlist('songselect')

    for songid in songlist:
        g.database.execute("""DELETE FROM song_playlist WHERE Song_id=%s AND Playlist_id=%s """ %
                          (songid, playlistid))
        g.conn.commit()

    return redirect(url_for('playlist.playlistPage', playlistid=playlistid))


@playlist.route('/playlist/<playlistid>/recommend/', methods=['POST'])
def recommendPlaylist(playlistid):
  print request.form
  for name in request.form:
  
    if request.form[name] == "Recommend":
  
      g.database.execute("SELECT max(Recommend_id) FROM recommend");
      recommendid = g.database.fetchone()

      if recommendid[0] == None:
        recommendid = 0
      else:
        recommendid = recommendid[0] + 1

      print recommendid, session['userid'], name
      g.database.execute("INSERT INTO recommend VALUES(%s,%s,%s,CURDATE())", (recommendid,session['userid'],name))
      g.conn.commit()

      g.database.execute("INSERT INTO recommend_playlists(Playlist_id, Recommend_id) VALUES (%s,%s)", (playlistid, recommendid))
      g.conn.commit()


  return redirect(url_for('playlist.playlistPage', playlistid=playlistid))