from flask import Blueprint, render_template, request, redirect, url_for
from flask import g, abort
from flask import session
from Forms import searchForm

artist = Blueprint('artist',__name__,template_folder='templates')


def getArtistdata(artistid):
  Artists = []
  g.database.execute("""SELECT Artist_name, Begin_date_year, End_date_year, Last_updated,Artist_id FROM artists WHERE Artist_id= "%s" """ % artistid)
  for row in g.database.fetchall():
    data = {}
    data['name'] = row[0]
    data['id']=row[4]
    data['begin'] = row[1]
    data['end'] = row[2]
    data['update'] = row[3]
    print data
    Artists.append(data)
  return Artists

def getLikes(artistid):
  g.database.execute("SELECT likes FROM artists where Song_id='%s'" % artistid)
  return g.database.fetchone()[0]

def getSongArtist(artistid):
  song = []
  g.database.execute("SELECT Song_id FROM song_artists WHERE Artist_id='%s'" % artistid)
  for songid in g.database.fetchall():
    data = {}
    g.database.execute("SELECT Song_id,Song_title FROM songs WHERE Song_id=%s" % songid[0])
    for temp in g.database.fetchall():
      data['songid'] = temp[0]
      data['songname'] = temp[1]
      song.append(data)

  return song


@artist.route('/artist/<artistid>')
def artistPage(artistid):
  if g.database.execute("SELECT * FROM artists WHERE Artist_id=%s" % artistid) == 0:
    if 'username' in session:
        abort(404)
    else:
      abort("You must be logged in to see this page.")
  return render_template('artistpage/index.html', songs=getSongArtist(artistid),
              artists=getArtistdata(artistid),
              artistid=artistid, form6=searchForm(prefix='form6'))

