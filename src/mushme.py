#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src import app
import os
from flask import Flask, render_template, session, request, flash, url_for, redirect
from Forms import ContactForm, LoginForm, editForm, ReportForm, CommentForm
from flask.ext.mail import Message, Mail
from api import API
from models import database, conn

import hashlib

mail = Mail()
mail.init_app(app)

#For the collector script.
app.register_blueprint(API);

@app.route('/')
def index():
    session["login"] = False
    session["signup"] = False
    return render_template('homepage/index.html', form1=LoginForm(prefix='form1'), form2=ContactForm(prefix='form2'))


@app.route('/login', methods=['POST'])
def login():
    session["login"] = True
    session["signup"] = False
    if request.method == 'POST':
        loginform = LoginForm(request.form, prefix='form1')

        if loginform.validate_on_submit():
            check_login = database.execute("SELECT User_id from MuShMe.entries WHERE Email_id='%s' AND Pwdhash='%s'" %
                                            (loginform.email.data, hashlib.sha1(loginform.password.data).hexdigest()))
            if check_login:
                userid= database.fetchone()
                for uid in userid:
                    return redirect(url_for('userProfile', userid=uid, form3=editForm(prefix='form3')))
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
        check_signup = database.execute("INSERT into MuShMe.entries (Username,Email_id,Pwdhash,Name) VALUES ('%s','%s','%s','%s')" % 
                                        (contactform.username.data,
                                        contactform.email.data,
                                        hashlib.sha1(contactform.password.data).hexdigest(),
                                        contactform.name.data))
        if check_signup == True:
            conn.commit()
            database.execute("SELECT User_id from entries WHERE Email_id='%s' AND Pwdhash='%s'" %
                                        (contactform.email.data, hashlib.sha1(contactform.password.data).hexdigest()))
            user_id = database.fetchone()
            for uid in user_id:
                return redirect(url_for('userProfile',userid=uid, form3=editForm(prefix='form3')))
    else:
        flash("Please Enter Valid Data !")
    return render_template('homepage/index.html', form1=LoginForm(prefix='form1'), form2=contactform)


#All your profile are belong to us.
@app.route('/artist/<aprofileid>')
def artistProfile(aprofileid):
    return render_template('artistpage/index.html')

@app.route('/user/<userid>',methods=['POST','GET'])
def userProfile(userid):
    uid=userid
    if request.method != 'POST':
        database.execute("SELECT Username from entries WHERE User_id='%s' " % userid )
        session["UserName"]=database.fetchone()
        database.execute("SELECT Name from entries WHERE User_id='%s' " % userid )
        session["Name"]=database.fetchone()
        database.execute("SELECT DOB from entries WHERE User_id='%s' " % userid )
        session["dob"]=database.fetchone()

        database.execute("SELECT User_id2 from friends WHERE User_id1='%s' " % userid)
        for user in database.fetchall():
            database.execute("SELECT Username from entries WHERE User_id='%s' " % user)
            friendName = database.fetchone()
            return friendName

        database.execute("SELECT Playlist_id from user_playlist WHERE User_id='%s' " % userid)
        for playlist in database.fetchall():
            database.execute("SELECT Playlist_name from playlists WHERE Playlist_id='%s' " % playlist)
            playlistName = database.fetchone()
            return playlistName

        database.execute("SELECT Song_id from user_song WHERE User_id='%s' " % userid)
        for song in database.fetchall():
            database.execute("SELECT Song_title from songs WHERE Song_id='%s' " % song)
            songName = database.fetchone()
            return songName
        return render_template('userprofile/index.html', form5=CommentForm(prefix='form5'), form3=editForm(prefix='form3'))

    if request.method == 'POST':
        return render_template(url_for('editName', userid=uid))



@app.route('/user/edit',methods=['POST','GET'])
def editName(userid):
    if request.method == 'POST':
        editform = editForm(request.form, prefix='form3')

        if editForm.validate_on_submit():
            check_edit = database.execute("UPDATE IN MuShMe.entries SET Name='%s',dob='%s' WHERE User_id='%s')" % (editform.name.data, editform.dob.data, userid))
            return render_template('userprofile/index.html', form5=CommentForm(prefix='form5'), form3=editform)
    else:
        return render_template('userprofile/index.html', form5=CommentForm(prefix='form5'), form3=editForm(prefix='form3'))

@app.route('/user/<userid>/report',methods=['POST','GET'])
def reportUser(userid):
    if request.method == POST:
        reportform = ReportFrom(request.form, prefix='form4')

        if reportform.validate_on_submit():
            check_report = database.execute("UPDATE IN MuShMe.entries SET Name='%s',dob='%s' WHERE User_id='%s')" % 
                                            (editform.name.data,
                                                editform.dob.data), (userid))
            #return render_template('userprofile/edit.html',userid)

@app.route('/song/<songid>')
def songPage(songid):
    return render_template('songpage/index.html')

@app.route('/playlist/<playlistid>')
def playlistPage(playlistid):
    return render_template('playlist/index.html')

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

@app.route('/testdb')
def testdb():
    return "hello"

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
            use_reloader=use_debugger, host='0.0.0.0')