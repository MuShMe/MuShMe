#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src import app
import os
import shutil
from flask import Flask, render_template, session, request, flash, url_for, redirect
from Forms import ContactForm, LoginForm, editForm, ReportForm, CommentForm, searchForm, AddPlaylist
from flask.ext.mail import Message, Mail
from api import API
from songs import SONG
from playlist import playlist
from admin import admin
from artist import artist
import pymysql
import hashlib
from flask import g

mail = Mail()
mail.init_app(app)

#For the collector script.
app.register_blueprint(API);
#For the songs
app.register_blueprint(SONG);
#For the playlist
app.register_blueprint(playlist);
#for the admin pages
app.register_blueprint(admin);
#for the artist pages
app.register_blueprint(artist);


@app.route('/')
def index():
    session["login"] = False
    session["signup"] = False
    session["logged_in"] = False
    return render_template('homepage/index.html', form1=LoginForm(prefix='form1'), form2=ContactForm(prefix='form2'))

#For database connections.
@app.before_request
def before_request():
    g.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='crimson', db='MuShMe', charset='utf8') 
    g.database = g.conn.cursor()


@app.teardown_request
def teardown_request(exception):
    g.conn.close()


@app.route('/login', methods=['POST'])
def login():
    session["""login"""] = True
    session["""signup"""] = False
    if request.method == 'POST':
        loginform = LoginForm(request.form, prefix='form1')

        if loginform.validate_on_submit():
            check_login = g.database.execute("""SELECT User_id from MuShMe.entries WHERE Email_id="%s" AND Pwdhash="%s" """ %
                                            (loginform.email.data, hashlib.sha1(loginform.password.data).hexdigest()))
            if check_login:
                userid= g.database.fetchone()
                g.database.execute("""UPDATE MuShMe.entries SET Last_Login=CURRENT_TIMESTAMP() WHERE User_id="%s" """ % (userid))
                g.conn.commit()
                for uid in userid:
                    session['userid'] = uid
                    g.database.execute("""SELECT Username from MuShMe.entries WHERE User_id="%s" """ % uid )
                    session['UserName']=g.database.fetchone()
                    g.database.execute("""SELECT Privilege FROM MuShMe.entries WHERE User_id="%s" """ % uid)
                    session['privilege'] = g.database.fetchone()[0]
                    g.database.execute("""SELECT Profile_Pic FROM MuShMe.entries WHERE User_id="%s" """ % uid)
                    session['profilepic'] = g.database.fetchone()[0]
                    g.database.execute("""SELECT Name from MuShMe.entries WHERE User_id="%s" """ % uid )
                    session["Name"]=g.database.fetchone()
                    g.database.execute("""SELECT DOB from MuShMe.entries WHERE User_id="%s" """ % uid )
                    session["dob"]=g.database.fetchone()
                    session['logged_in'] = True
                    session['logged_in']=True
                    #print uid
                    #print userid
                    return redirect(url_for('userProfile', userid=uid))
            else:
                flash("""Incorrect Email-Id or Password""")

        else:
            flash("""Incorrect Email-Id or Password""")
        return render_template('homepage/index.html', form1=loginform, form2=ContactForm(prefix='form2'))
    else:
        return redirect(url_for(('index')))


@app.route('/signup', methods=['POST'])
def signup():
    session["signup"] = True    
    session["login"] = False
    contactform = ContactForm(request.form, prefix='form2')

    if validate(contactform.email.data,contactform.username.data):
        check_signup = g.database.execute("""INSERT into MuShMe.entries (Username,Email_id,Pwdhash,Name) VALUES ("%s","%s","%s","%s")""" % 
                                        (contactform.username.data,
                                        contactform.email.data,
                                        hashlib.sha1(contactform.password.data).hexdigest(),
                                        contactform.name.data))
        if check_signup:
            g.conn.commit()
            g.database.execute("""SELECT User_id from MuShMe.entries WHERE Email_id="%s" AND Pwdhash="%s" """ %
                                        (contactform.email.data, hashlib.sha1(contactform.password.data).hexdigest()))
            user_id = g.database.fetchone()
            for uid in user_id:
                session['userid'] = uid
                g.database.execute("""SELECT Username from MuShMe.entries WHERE User_id="%s" """ % uid )
                session['UserName']=g.database.fetchone()[0]
                g.database.execute("""SELECT Privilege FROM MuShMe.entries WHERE User_id="%s" """ % uid)
                session['privilege'] = g.database.fetchone()[0]
                g.database.execute("""SELECT Profile_Pic FROM MuShMe.entries WHERE User_id="%s" """ % uid)
                session['profilepic'] = g.database.fetchone()[0]
                session['logged_in'] = True
                g.database.execute("""SELECT Name from MuShMe.entries WHERE User_id="%s" """ % uid )
                session["Name"]=g.database.fetchone()
                g.database.execute("""SELECT DOB from MuShMe.entries WHERE User_id="%s" """ % uid )
                session["dob"]=g.database.fetchone()
                newPlaylist = session['UserName'] + ' default collection'
                g.database.execute("""INSERT INTO MuShMe.playlists (Playlist_name, User_id) VALUES ("%s","%s")""" % (newPlaylist,uid))
                g.conn.commit()
                return redirect(url_for('userProfile',userid=uid))
        else:
            flash("Please enter valid data !")
    else:
        flash("Username or Email has been taken")
    return render_template('homepage/index.html', form1=LoginForm(prefix='form1'), form2=contactform)

def validate(email,username):
    email = g.database.execute(""" SELECT * from MuShMe.entries where Email_id="%s" """ % email)
    name = g.database.execute(""" SELECT * from MuShMe.entries where Username="%s" """ % username)
    if email or name:
        return False
    else:
        return True

@app.route('/user/<userid>',methods=['GET'])
def userProfile(userid):
    if session['logged_in'] == False:
        return render_template('error.html'), 404
    else:
        if request.method == 'GET':
            User=getUserData(userid)
            return render_template('userprofile/index.html', userid=userid,
                form4=CommentForm(prefix='form4'), form3=editForm(prefix='form3'),
                form6=searchForm(prefix='form6'), form5=ReportForm(prefix='form5'),form7=AddPlaylist(prefix='form7'),
                friend=getFriend(userid), playlist=getPlaylist(userid), User=getUserData(userid), Comments=getComments(userid),
                song=getSong(userid), Recommends=getRecommend(userid), Requests=getRequest(userid),frnd=checkFriend(userid,User))

def checkFriend(userid,User):
    friendName =[]
    g.database.execute("""SELECT User_id2 from friends WHERE User_id1="%s" """ % (userid))
    for user in g.database.fetchall():
        data = {}
        g.database.execute("""SELECT Username, User_id from MuShMe.entries WHERE User_id="%s" """ % user[0])
        for a in g.database.fetchall():
            data['friendname']=a[0]
            data['friendid']=a[1]
        friendName.append(data)
    for f in friendName:
        a=g.database.execute("""SELECT User_id2 from friends WHERE User_id1="%s" and User_id2="%s" """ % (userid,f['friendid']))
        b=g.database.execute("""SELECT User_id2 from friends WHERE User_id2="%s" and User_id1="%s" """ % (userid,f['friendid']))
        if a or b:
            return True
        elif userid == f['friendid']:
            return True
        else:
            return False

    g.database.execute("""SELECT User_id1 from friends WHERE User_id2="%s" """ % userid)
    for user in g.database.fetchall():
        data = {}
        g.database.execute("""SELECT Username, User_id from MuShMe.entries WHERE User_id="%s" """ % user[0])
        for a in g.database.fetchall():
            data['friendname']=a[0]
            data['friendid']=a[1]
        friendName.append(data)
    for f in friendName:
        a=g.database.execute("""SELECT User_id2 from friends WHERE User_id2="%s" and User_id1="%s" """ % (userid,f['friendid']))
        b=g.database.execute("""SELECT User_id2 from friends WHERE User_id1="%s" and User_id2="%s" """ % (userid,f['friendid']))
        if a or b:
            return True
        elif userid == f['friendid']:
            return True
        else:
            return False


def getComments(userid):
    g.database.execute("SELECT Comment_id FROM user_comments WHERE User_id=%s ORDER BY Comment_id DESC" % (userid))
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

def getFriend(userid):
    friendName =[]
    g.database.execute("""SELECT User_id2 from friends WHERE User_id1="%s" """ % userid)
    for user in g.database.fetchall():
        data = {}
        g.database.execute("""SELECT Username, User_id from MuShMe.entries WHERE User_id="%s" """ % user[0])
        for a in g.database.fetchall():
            data['friendname']=a[0]
            data['friendid']=a[1]
        friendName.append(data)
    g.database.execute("""SELECT User_id1 from friends WHERE User_id2="%s" """ % userid)
    for user in g.database.fetchall():
        data = {}
        g.database.execute("""SELECT Username, User_id from MuShMe.entries WHERE User_id="%s" """ % user[0])
        for a in g.database.fetchall():
            data['friendname']=a[0]
            data['friendid']=a[1]
        friendName.append(data)
    return friendName

def getPlaylist(userid):
    playlist = []
    g.database.execute("""SELECT Playlist_name,Playlist_id from MuShMe.playlists WHERE User_id="%s" """ % userid)
    for p in g.database.fetchall():
        data = {}
        data['pname']=p[0]
        data['pid']=p[1]
        playlist.append(data)
    return playlist

def getSong(userid):
    songName = []
    g.database.execute("""SELECT Song_id from MuShMe.user_song WHERE User_id=%s """ % userid)
    for song in g.database.fetchall():
        data = {}
        g.database.execute("""SELECT Song_title,Song_id from MuShMe.songs WHERE Song_id="%s" """ % song)
        for a in g.database.fetchall():
            data['songname']=a[0]
            data['songid']=a[1]
        songName.append(data)
    return songName

def getUserData(userid):
    User = []
    g.database.execute(""" SELECT Username,User_id,Profile_pic,Privilege,Email_id,Name,DOB from entries where User_id="%s" """ % userid)
    for a in g.database.fetchall():
        data={}
        data['username']=a[0]
        data['userid']=a[1]
        data['profilepic'] = a[2]
        data['privilege']=a[3]
        data['email']=a[4]
        data['name']=a[5]
        data['dob']=a[6]
        User.append(data)
    return User

def getRecommend(userid):
    recommend =[]
    g.database.execute(""" SELECT Recommend_id,User_id_from,User_id_to from recommend where User_id_to="%s" """ % userid)
    for a in g.database.fetchall():
        data={}
        data['rid']=a[0]
        data['userfrom'] = a[1]
        data['userto']=a[2]
        g.database.execute(""" SELECT Song_id from recommend_songs where Recommend_id="%s" """ % a[0])
        songid = g.database.fetchone()[0]
        data['song'] = []
        g.database.execute(""" SELECT Song_title,Song_Album,Genre,Publisher from songs where Song_id="%s" """ % songid)
        for song in g.database.fetchall():
            d = {}
            d['title']=song[0]
            d['album'] = song[1]
            d['genre'] = song[2]
            d['publisher'] = song[3]
            d['songid'] = songid
            data['song'].append(d)

        g.database.execute(""" SELECT Playlists_id from recommend_playlists where Recommend_id="%s" """ % a[0])
        playlistid = g.database.fetchone()[0]
        data['playlist'] = []
        g.database.execute(""" SELECT Playlist_name,Playlist_id,User_id from playlists where Song_id="%s" """ % playlistid)
        for p in g.database.fetchall():
            d= {}
            d['pname']=p[0]
            d['pid']=p[1]
            g.database.execute(""" SELECT Username, Name,User_id from MuShMe.entries WHERE User_id="%s" """ % p[2])
            for k in g.database.fetchall():
                d['username']=k[0]
                d['uname']=k[1]
                d['userid']=k[2]
            data['playlist'].append(d)

        recommend.append(data)
    return recommend

def getRequest(userid):
    request =[]
    g.database.execute(""" SELECT Request_id,Request_from,Request_to,Status from requests where Request_to="%s" """ % userid)
    for a in g.database.fetchall():
        data={}
        data['reqid']=a[0]
        data['reqfrom'] = a[1]
        data['reqto']=a[2]
        data['status']=a[3]

        data['reqfromuser'] = []
        g.database.execute(""" SELECT User_id,Username,Name from entries where User_id='%s' """ % a[1])
        for i in g.database.fetchall():
            d={}
            d['userid'] = i[0]
            d['username'] = i[1]
            d['name'] = i[2]
            data['reqfromuser'].append(d)
        print data

        request.append(data)
    return request


@app.route('/user/<userid>/edit',methods=['POST','GET'])
def editName(userid):
    if request.method == 'POST':
        editform = editForm(request.form, prefix='form3')
        uid = userid
        g.database.execute("""UPDATE MuShMe.entries SET Name="%s" WHERE User_id="%s" """ % (editform.name.data, userid))
        g.conn.commit()
        if upload_file(userid,editform):
            g.database.execute("""UPDATE MuShMe.entries SET Profile_pic="%s" WHERE User_id="%s" """ % (app.config['UPLOAD_FOLDER'], userid))
        g.conn.commit()
        return redirect(url_for('userProfile',userid=userid))
    else:
        return redirect(url_for('userProfile', userid=userid))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/user/<userid>/file', methods=['GET', 'POST'])
def upload_file(userid,editform):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', userid=userid))


@app.route('/user/<userid>/show/<filename>')
def uploaded_file(userid,filename):
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    return redirect(url_for('editName',filename = filename,userid=userid))

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/user/<rcvrid>.<senderid>/comment',methods=['POST','GET'])
def comment(rcvrid, senderid):
    if request.method == 'POST':
        commentform = CommentForm(request.form, prefix='form4')
        #print senderid
        #print rcvrid
        if commentform.comment.data:
            query = ("""INSERT INTO MuShMe.comments (comment_type, Comment, User_id) VALUES ("%s","%s","%s") """ % ('U',commentform.comment.data, senderid))
            print query
            g.database.execute(query)
            g.conn.commit()
        
            g.database.execute("""SELECT Comment_id from MuShMe.comments WHERE Comment="%s" """ % (commentform.comment.data))
            data = g.database.fetchone()[0]
            #print data
            enter_comment = g.database.execute("""INSERT INTO MuShMe.user_comments (Comment_id, User_id) VALUES ("%s","%s")""" % (data,rcvrid))
            if enter_comment:
                g.conn.commit()
                g.database.execute("""SELECT User_id FROM MuShMe.user_comments WHERE Comment_id="%s" """ % data)
                #print g.database.fetchone()[0]
        
        return redirect(url_for('userProfile', userid=rcvrid))

@app.route('/user/<userid>/<commentid>/report',methods=['POST','GET'])
def report(userid,commentid):
    if request.method == 'POST':
        reportform = ReportForm(request.form, prefix='form5')

        print reportform.report.data
        check_report = g.database.execute("""INSERT INTO MuShMe.complaints (Complain_type, Complain_description, Comment_id,reported_by) VALUES ("%s","%s","%s","%s") """ % (reportform.report.data, reportform.other.data, commentid, session['userid'] ))
        if check_report == True:
            g.conn.commit()
        return redirect(url_for('userProfile', userid=userid))
    else:
        return redirect(url_for('userProfile', userid=userid))

@app.route('/user/<uidto>.<uidfrom>/request',methods=['POST'])
def sendrequest(uidto,uidfrom):
    if request.method == 'POST':
        if requestvalidate(uidfrom,uidto):
            query=(""" INSERT INTO requests (Request_from,Request_to,Status) VALUES ("%s","%s","%s") """ % (uidfrom,uidto,1))
            g.database.execute(query)
            g.conn.commit()
        return redirect(url_for('userProfile', userid=uidto))

@app.route('/user/<userto>.<userfrom>/accept',methods=['POST'])
def acceptrequest(userto,userfrom):
    if request.method == 'POST':
        query=(""" UPDATE requests SET Status="%s" WHERE Request_from="%s" and Request_to="%s" """ % (0,userfrom,userto))
        g.database.execute(query)
        g.conn.commit()

        query = (""" INSERT INTO friends Values ("%s","%s") """ % (userfrom,userto))
        g.database.execute(query)
        g.conn.commit()
        return redirect(url_for('userProfile', userid=userto))

@app.route('/user/<userto>.<userfrom>/reject',methods=['POST'])
def rejectrequest(userto,userfrom):
    if request.method == 'POST':
        query=(""" UPDATE requests SET Status="%s" WHERE Request_from="%s" and Request_to="%s" """ % (-1,userfrom,userto))
        g.database.execute(query)
        g.conn.commit()
        return redirect(url_for('userProfile', userid=userto))

def requestvalidate(userfrom,userto):
    check = g.database.execute(""" SELECT Status from requests where Request_to="%s" and Request_from="%s" """ % (userfrom,userto))
    if check and g.database.fetchone()[0]=='-1' and userfrom!=userto:
        return False
    else:
        return True

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method == 'POST':
        searchform = searchForm(prefix='form6')
        #print 'f'
        search_fname = []
        search_song= []
        search_friend = []
        search_playlist =[]
        search_artist = []
        check_song = g.database.execute("""SELECT Song_title,Song_Album,Genre,Publisher,Song_id from MuShMe.songs WHERE Song_title="%s" """ % ( searchform.entry.data ))
        for a in g.database.fetchall():
            data={}
            data['title']=a[0]
            data['album']=a[1]
            data['genre']=a[2]
            data['publisher']=a[3]
            data['songid']=a[4]
            search_song.append(data)
        check_artist = g.database.execute("""SELECT Artist_name, Artist_id from MuShMe.artists WHERE Artist_name="%s" """ % ( searchform.entry.data ))
        for a in g.database.fetchall():
            data = {}
            data['artistname']=a[0]
            data['artistid']=a[1]
            search_artist.append(data)
        check_friend = g.database.execute("""SELECT Username, Name, Profile_pic, User_id from MuShMe.entries WHERE Username="%s" or Name="%s" """ % ( searchform.entry.data, searchform.entry.data ))
        for a in g.database.fetchall():
            data = {}
            data['username']=a[0]
            data['name']=a[1]
            data['profilepic']=a[2]
            data['userid']=a[3]
            print data
            search_friend.append('data')
        check_playlist = g.database.execute("""SELECT Playlist_name,User_id, Playlist_id from MuShMe.playlists WHERE Playlist_name="%s" """ % ( searchform.entry.data ))
        for a in g.database.fetchall():
            data = {}
            data['pname']=a[0]
            data['pid']=a[2]
            g.database.execute(""" SELECT Username, Name from MuShMe.entries WHERE User_id="%s" """ % a[1])
            for k in g.database.fetchall():
                data['username']=k[0]
                data['uname']=k[1]
            search_playlist.append(data)
        length = len(search_playlist) + len(search_song) + len(search_friend) + len(search_artist) + len(search_fname)

        return render_template('searchpage/search.html', entry=searchform.entry.data,form6=searchForm(prefix='form6'),
             search_song=search_song, search_artist=search_artist,friends=search_friend,
             search_playlist=search_playlist,length = length)
    else:
        return render_template('searchpage/search.html',form6=searchForm(prefix='form6'))

@app.route('/user/<userid>',methods=['POST','GET'])
def uploadSong(userid):
    if request.method == 'POST':
        reportform = ReportForm(request.form, prefix='form5')

        check_report = g.database.execute("""INSERT INTO MuShMe.complaints (Complain_type, Complain_description, Comment_id) VALUES ("%s","%s","%s") """ % (spamNumber, reportform.spam.data, session['comment_id'], session['userid'] ))
        if check_comment == True:
            g.conn.commit()
        return redirect(url_for('userProfile',userid=userid))
    else:
        return redirect(url_for('userProfile',userid=userid))



@app.route('/user/<userid>/addplaylist',methods=['POST'])
def addplaylist(userid):
    if request.method=='POST':
        addplaylistform = AddPlaylist(prefix='form7')
        g.database.execute("""INSERT INTO MuShMe.playlists (Playlist_name, User_id) VALUES ("%s","%s")""" % (addplaylistform.add.data,userid))
        g.conn.commit()
        return redirect(url_for('userProfile',userid=userid))

#All your profile are belong to us.
@app.route('/artist/<artistid>')
def artistProfile(artistid):
    return render_template('artistpage/index.html',form6=searchForm(prefix='form6'))

#To handle 404 not found errors
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('error.html'), 404

@app.route('/termsofservices')
def tos():
    return render_template('tos.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/changepwd')
def changepwd():
    return render_template('changepwd.html')

@app.route('/logout')
def logout(): 
    if 'email' not in session: 
        return render_template('error.html')
    
    session['logged_in']=False
    return render_template('login.html')


if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1', 'server-error@example.com', app.config['DEFAULT_MAIL_SENDER'], 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    from logging import FileHandler
    file_handler = FileHandler('log.txt')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

    from logging import Formatter
mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))

if __name__ == """__main__""":
    # To allow aptana to receive errors, set use_debugger=False
    app = create_app(config="""config.yaml""")

    if app.debug: use_debugger = True
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger, threaded=True, port=8080)
