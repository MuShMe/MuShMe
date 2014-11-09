from flask import Blueprint
from flask import g, redirect, render_template
from Forms import ContactForm

playlist = Blueprint('playlist',__name__,template_folder='templates')


def getPlaylistName(playlistid):
    g.database.execute("""SELECT Playlist_name FROM playlists WHERE Playlist_id=%s""", (playlistid))
    playlistname= g.database.fetchone()

    if playlistname == None:
        return ""
    else:
        return playlistname[0]


def getUserData(playlistid):
    g.database.execute("""SELECT User_id FROM playlists WHERE Playlist_id=%s""", (playlistid))
    userid = g.database.fetchone()[0]
    g.database.execute("""SELECT User_name FROM entries WHERE User_id=%s""", (userid))
    username = g.database.fetchone()[0]
    data = {}
    
    data['userid'] = userid
    data['username'] = username

    return data


def getLikes(playlistid):
  g.database.execute("""SELECT count(*) FROM user_like_playlist WHERE Playlist_id='%s'""", (playlistid))
  likes = g.database.fetchone()
  if likes==None:
    return 0
  else:
    return likes[0]


def getComments(playlistid):
    g.database.execute("SELECT Comment_id FROM playlist_comments WHERE Playlist_id=%s ORDER BY DESC", (playlistid))
    commentids = g.database.fetchall()
    retval = []

    for commentid in commentids:
        g.database.execute("SELECT Comment, User_id FROM comments WHERE Commment_id=%s", (commentid[0]))
        commentdata = g.database.fetchone()

        data = {}
        data['comment'] = commentdata[0]
        data['userid'] = commentdata[1]

        g.database.execute("SELECT User_name FROM entries WHERE User_id=%s", (data['userid']))
        data['username'] = g.database.fetchone()[0]
        retval.append(data)

    return retval



def getPlaylistSongs(playlistid):
    g.database.execute("SELECT Song_id from song_playlist WHERE Song_id=%s", (playlistid))
    songs = g.database.fetchall()

    retval = []

    for song in songs:
        g.database.execute("SELECT Song_name,Album_id FROM songs WHERE Song_id=%s", (song[0]))
        songdata = g.database.fetchone()
        
        data = {}
        data['songname'] = songdata[0]
        data['songid'] = song[0]
        g.database.execute("SELECT Album_pic FROM albums WHERE Album_id=%s", (songdata[1]))
        data['albumart'] = g.database.fetchone()[0]
        retval.append(data)

    return retval


@playlist.route('/playlist/<playlistid>/addcomment/', methods=['POST'])
def addcommentplaylist(playlistid):
    g.database.execute("SELECT max(Comment_id) FROM comments")
    pk = g.database.fetchone()[0]

    if pk == None:
        pk = 1
    else:
        pk = pk + 1

    comment_type = "S"
    g.database.execute("""INSERT INTO comments VALUES (%s, "%s", "%s",%s, %s)""", (pk,comment_type, request.form['comment'],'0', session['userid']))
    g.conn.commit()
    g.database.execute("""INSERT INTO playlist_comments VALUES (%s,%s)""", (songid,pk))
    g.conn.commit()
    return redirect(url_for('.playlistPage', songid=songid))


@playlist.route('/playlist/<playlistid>')
def playlistPage(playlistid):
    return render_template('playlist/index.html',
                            playlistid=playlistid, 
                            pname=getPlaylistName(playlistid), 
                            puserdata=getUserData(playlistid),
                            likes = getLikes(playlistid),
                            commentform= CommentForm(playlistid),
                            songs = getPlaylistSongs(playlistid),
                            comments=getComments(playlistid))
