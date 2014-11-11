#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src import app
import os
from flask import Flask, render_template, session, request, flash, url_for, redirect
from Forms import ContactForm, LoginForm, editForm, ReportForm, CommentForm, searchForm
from flask.ext.mail import Message, Mail
from api import API
from songs import SONG
from playlist import playlist
from admin import admin
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


@app.route('/')
def index():
    session["login"] = False
    session["signup"] = False
    session["logged"] = False
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
    session["login"] = True
    session["signup"] = False
    if request.method == 'POST':
        loginform = LoginForm(request.form, prefix='form1')

        if loginform.validate_on_submit():
            check_login = g.database.execute("SELECT User_id from MuShMe.entries WHERE Email_id='%s' AND Pwdhash='%s'" %
                                            (loginform.email.data, hashlib.sha1(loginform.password.data).hexdigest()))
            if check_login:
                userid= g.database.fetchone()
                g.database.execute("UPDATE MuShMe.entries SET Last_Login=CURRENT_TIMESTAMP() WHERE User_id='%s'" % (userid))
                g.conn.commit()
                for uid in userid:
                    session['User_id'] = uid
                    session['logged']=True
                    return redirect(url_for('userProfile', userid=uid))
            else:
                flash("Incorrect Email-Id or Password")

        else:
            flash("Incorrect Email-Id or Password")
        return render_template('homepage/index.html', form1=loginform, form2=ContactForm(prefix='form2'))
    else:
        return redirect(url_for(('index')))


@app.route('/signup', methods=['POST'])
def signup():
    session["signup"] = True    
    session["login"] = False
    contactform = ContactForm(request.form, prefix='form2')

    if contactform.validate_on_submit():
        check_signup = g.database.execute("INSERT into MuShMe.entries (Username,Email_id,Pwdhash,Name) VALUES ('%s','%s','%s','%s')" % 
                                        (contactform.username.data,
                                        contactform.email.data,
                                        hashlib.sha1(contactform.password.data).hexdigest(),
                                        contactform.name.data))
        if check_signup:
            g.conn.commit()
            g.database.execute("SELECT User_id from MuShMe.entries WHERE Email_id='%s' AND Pwdhash='%s'" %
                                        (contactform.email.data, hashlib.sha1(contactform.password.data).hexdigest()))
            user_id = g.database.fetchone()
            for uid in user_id:
                session['User_id'] = uid
                session['logged'] = True
                g.database.execute("INSERT INTO MuShMe.playlists (Playlist_name, User_id) VALUES ('%s','%s')" % ('Recently Added',uid))
                g.conn.commit()
                return redirect(url_for('userProfile',userid=uid))
        else:
            flash("Please Enter Valid Data !")
    else:
        flash("Please Enter Valid Data !")
    return render_template('homepage/index.html', form1=LoginForm(prefix='form1'), form2=contactform)



@app.route('/user/<userid>',methods=['POST','GET'])
def userProfile(userid):
    if session['logged'] == False:
        return render_template('error.html'), 404
    else:
        if request.method != 'POST':
            friendName = []
            comment = []
            username = []
            songName = []
            session['userid'] = userid
            g.database.execute("SELECT Username from MuShMe.entries WHERE User_id='%s' " % userid )
            session["UserName"]=g.database.fetchone()
            g.database.execute("SELECT Name from MuShMe.entries WHERE User_id='%s' " % userid )
            session["Name"]=g.database.fetchone()
            g.database.execute("SELECT DOB from MuShMe.entries WHERE User_id='%s' " % userid )
            session["dob"]=g.database.fetchone()
            g.database.execute("SELECT Privilege FROM MuShMe.entries WHERE User_id='%s'" % userid)
            session['privilege'] = g.database.fetchone()[0]
            g.database.execute("SELECT Profile_Pic FROM MuShMe.entries WHERE User_id='%s' " % userid)
            session['profilepic'] = g.database.fetchone()[0]

            g.database.execute("SELECT User_id2 from friends WHERE User_id1='%s' " % userid)
            i=0
            for user in g.database.fetchall():
                g.database.execute("SELECT Username from MuShMe.entries WHERE User_id='%s' " % user)
                friendName.append(g.database.fetchone()[0])
                i=i+1
                #return friendName[i]
                
            g.database.execute("SELECT Playlist_name from MuShMe.playlists WHERE User_id='%s' " % userid)
            playlist = g.database.fetchall()
                #return playlist

            g.database.execute("SELECT Comment_id from MuShMe.comments WHERE User_id='%s' " % userid)
            i=0
            for c in g.database.fetchall():
                g.database.execute("SELECT Comment from MuShMe.comments WHERE Comment_id='%s' ORDER BY Comment_id desc" % c)
                comment.append(g.database.fetchone()[0])
                g.database.execute("SELECT User_id from MuShMe.comments WHERE Comment_id='%s' ORDER BY Comment_id desc" % c)
                uid=g.database.fetchone()[0]
                #print uid
                g.database.execute("SELECT Username from MuShMe.entries WHERE User_id='%s' " % uid)
                username.append(g.database.fetchone()[0])
                #print username[i]
                i = i+1

            g.database.execute("SELECT Song_id from MuShMe.user_song WHERE User_id='%s' " % userid)
            i=0
            for song in g.database.fetchall():
                g.database.execute("SELECT Song_title from MuShMe.songs WHERE Song_id='%s' " % song)
                songName.append(g.database.fetchone()[0])
                i = i+1
                #return songName[i]

            return render_template('userprofile/index.html', form4=CommentForm(prefix='form4'), form3=editForm(prefix='form3'),form6=searchForm(prefix='form6'), form5=ReportForm(prefix='form5'), friend=friendName, playlist=playlist, user=username, comment=comment, song=songName)

@app.route('/user/<userid>/edit',methods=['POST','GET'])
def editName(userid):
    if request.method == 'POST':
        editform = editForm(request.form, prefix='form3')

        check_edit = g.database.execute("UPDATE MuShMe.entries SET Name='%s' WHERE User_id='%s' " % (editform.name.data, userid))
        if check_edit:
            g.conn.commit()
            return render_template('userprofile/index.html', friend=friendName, playlist=playlist, user=username, comment=comment, song=songName, userid=session['userid'],form4=CommentForm(prefix='form4'), form3=editform, form6=searchForm(prefix='form6'),form5=ReportForm(prefix='form5'))
        else:
            return render_template('error.html'), 404
    else:
        return redirect(url_for('userProfile', userid=session['userid']))
        
@app.route('/user/<userid>/comment',methods=['POST','GET'])
def comment(userid):
    if request.method == 'POST':
        commentform = CommentForm(request.form, prefix='form3')

        print commentform.comment.data
        g.database.execute("INSERT INTO MuShMe.comments (comment_type, Comment, User_id) VALUES ('%s','%s','%s') " % ('U',commentform.comment.data, session['userid']))
        g.conn.commit()
        
        g.database.execute("SELECT Comment_id from MuShMe.comments WHERE Comment='%s' " % (commentform.comment.data))
        data = g.database.fetchone()[0] 
        enter_comment = g.database.execute("INSERT INTO MuShMe.user_comments (Comment_id, User_id) VALUES ('%s','%s')" % (data,userid))
        
        return redirect(url_for('userProfile', userid=session['userid']))
    else:
        return redirect(url_for('userProfile', userid=session['userid']))

@app.route('/user/<userid>',methods=['POST','GET'])
def report(userid):
    if request.method == 'POST':
        reportform = ReportForm(request.form, prefix='form5')

        check_report = g.database.execute("INSERT INTO MuShMe.complaints (Complain_type, Complain_description, Comment_id) VALUES ('%s','%s','%s') " % (spamNumber, reportform.spam.data, session['comment_id'], session['userid'] ))
        if check_comment == True:
            g.conn.commit()
        return render_template('userprofile/index.html',userid=session['userid'], form4=CommentForm(prefix='form4'), form3=editForm(prefix='form3'), form6=searchForm(prefix='form6'), form5=reportform , friend=friendName, playlist=playlist, user=username, comment=comment, song=songName)
    else:
        return redirect(url_for('userProfile', userid=session['userid']))

@app.route('/search',methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('searchpage/search.html',form6=searchForm(prefix='form6'))
    else:
        searchform = searchForm(prefix='form6')
        check_song = g.database.execute("SELECT Song_title,Song_Album,Genre,Publisher from MuShMe.songs WHERE Song_title='%s'" % ( searchform.entry.data ))
        if check_song:
            search_song = g.database.fetchall()
        check_artist = g.database.execute("SELECT Artist_name from MuShMe.artists WHERE Artist_name='%s'" % ( searchform.entry.data ))
        if check_artist:
            search_artist = g.database.fetchall()
        check_friend = g.database.execute("SELECT Username, Name from MuShMe.entries WHERE Username='%s'" % ( searchform.entry.data ))
        if check_friend:
            search_friend = g.database.fetchall()
        check_playlist = g.database.execute("SELECT Playlist_name from MuShMe.playlists WHERE Playlist_name='%s'" % ( searchform.entry.data ))
        if check_playlist:
            search_playlist = g.database.fetchall()
        return render_template('searchpage/search.html',form6=searchForm(prefix='form6'))

@app.route('/user/<userid>',methods=['POST'])
def uploadSong(userid):
    if request.method == 'POST':
        reportform = ReportForm(request.form, prefix='form5')

        check_report = g.database.execute("INSERT INTO MuShMe.complaints (Complain_type, Complain_description, Comment_id) VALUES ('%s','%s','%s') " % (spamNumber, reportform.spam.data, session['comment_id'], session['userid'] ))
        if check_comment == True:
            g.conn.commit()
        return render_template('userprofile/index.html',userid=session['userid'], form4=commentform, form3=editForm(prefix='form3'))


#All your profile are belong to us.
@app.route('/artist/<aprofileid>')
def artistProfile(aprofileid):
    return render_template('artistpage/index.html')

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
    
    session['logged']=False
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

if __name__ == "__main__":
    # To allow aptana to receive errors, set use_debugger=False
    app = create_app(config="config.yaml")

    if app.debug: use_debugger = True
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger, threaded=True, port=8080)
