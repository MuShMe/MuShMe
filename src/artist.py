from flask import Blueprint, render_template, request, redirect, url_for
from flask import g, abort
from flask import session
from Forms import searchForm
from werkzeug import secure_filename
from werkzeug import SharedDataMiddleware
import os
from src import app

artist = Blueprint('artist',__name__,template_folder='templates')

UPLOAD_FOLDER = "img/ArtistPic/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER_ARTIST'] = 'src/static/' + UPLOAD_FOLDER

def getArtistdata(artistid):
  Artists = []
  g.database.execute("""SELECT Artist_name,Artist_pic, Begin_date_year, End_date_year, Last_updated,Artist_id FROM artists WHERE Artist_id= "%s" """ % artistid)
  for row in g.database.fetchall():
    data = {}
    data['name'] = row[0]
    data['id']=row[5]
    data['begin'] = row[2]
    data['end'] = row[3]
    data['update'] = row[4]
    data['profilepic'] = row[1]
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
      data['songart'] = getSongArt(data['songid'])
      song.append(data)

  return song

def getSongArt(songid):
    g.database.execute("SELECT Song_Album FROM songs WHERE song_id=%s", (songid))
    albumname = g.database.fetchone()[0]

    g.database.execute("SELECT Album_pic FROM albums WHERE Album_id=%s", (albumname))
    return g.database.fetchone()[0]


@artist.route('/artist/<artistid>')
def artistPage(artistid):
  if g.database.execute("SELECT * FROM artists WHERE Artist_id=%s" % artistid) == 0:
    if 'username' in session:
        abort(404)
    else:
      abort("You must be logged in to see this page.")
  return render_template('artistpage/index.html', songs=getSongArtist(artistid),
              artists=getArtistdata(artistid),
              artistid=artistid,
              form6=searchForm(prefix='form6'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@artist.route('/artist/<artistid>/file', methods=['POST'])
def upload_file(artistid):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_ARTIST'], filename))
            filepath = UPLOAD_FOLDER + filename
        g.database.execute("""UPDATE MuShMe.artists SET Artist_pic="%s" WHERE Artist_id="%s" """ % (filepath, artistid))
        g.conn.commit()
        return redirect(url_for('artist.artistPage', artistid=artistid))

app.add_url_rule('/artist/uploads/<filename>', 'uploaded_file',build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/artist/uploads':  'src/static/' + app.config['UPLOAD_FOLDER_ARTIST']   })

@artist.route('/artist/<artistid>/edit',methods= ['POST'])
def editArtist(artistid):
    if request.method == 'POST':
        print request.form
        if request.form['editname'] != '':
            g.database.execute("""UPDATE MuShMe.artists SET Artist_name=%s WHERE Artist_id=%s """, ([request.form['editname']], artistid))
            g.conn.commit()
        
        if request.form['begin_year'] != '0' and request.form['begin_month'] != '0' and request.form['begin_day'] != '0':
            g.database.execute("""UPDATE MuShMe.artists SET Begin_date_year="%s" WHERE Artist_id="%s" """ % 
                (request.form['begin_year'], artistid))
            g.conn.commit()

        if request.form['end_year'] != '0' and request.form['end_month'] != '0' and request.form['end_day'] != '0':
            g.database.execute("""UPDATE MuShMe.artists SET End_date_year="%s" WHERE Artist_id="%s" """ % 
                (request.form['end_year'], artistid))
            g.conn.commit()
        
        return redirect(url_for('artist.artistPage', artistid=artistid))
    else:
        return redirect(url_for('artist.artistPage', artistid=artistid))