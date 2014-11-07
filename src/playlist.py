from flask import Blueprint
from flask import g, redirect, render_template
from Forms import ContactForm

playlist = Blueprint('playlist',__name__,template_folder='templates')


def getPlaylistName(playlistid):
	g.database.execute("""SELECT Playlist_name FROM playlists WHERE Playlist_id=%s""", (playlistid))
	return g.database.fetchone()[0]


def getUserName(playlistid):
	g.database.execute("""SELECT User_id FROM playlists WHERE Playlist_id=%s""", (playlistid))
	userid = g.database.fetchone()[0]
	g.database.execute("""SELECT User_name FROM entries WHERE User_id=%s""", (userid))
	return g.database.fetchone()[0]

@playlist.route('/playlist/<playlistid>')
def playlistPage(playlistid):
    return render_template('playlist/index.html', pname=getPlaylistName(playlistid), 
    						pusername=getUserName(playlistid))