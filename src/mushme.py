#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src import app
import os
from flask import Flask, render_template, session, request, flash, url_for, redirect
from Forms import ContactForm, LoginForm
from flask.ext.mail import Message, Mail
from models import db, Entry
from api import API
 
mail = Mail()
mail.init_app(app)

#For the collector script.
app.register_blueprint(API);

@app.route('/')
def homepage():
    return render_template('homepage/index.html')

#All your profile are belong to us.
@app.route('/artist/<aprofileid>')
def artistProfile(aprofileid):
    return render_template('artistpage/index.html')

@app.route('/user/<userid>')
def userProfile(userid):
    return render_template('userprofile/index.html')

@app.route('/song/<songid>')
def songPage(songid):
    return render_template('songpage/index.html')


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

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
  
    if request.method == 'POST':
      if form.validate() == False:
        flash("Invalid Username or Password !")
        return redirect(url_for('login',form=form))
      else:
        session['email'] = form.email.data
        #session['username'] = session.execute(select(username).where(Entry.c.Email_id==[session['email']]))
        session['logged_in']=True
        return redirect(url_for('profile', success=True, session=True))
                   
    elif request.method == 'GET':
      return render_template('login.html', form=form, session=False)
  
@app.route('/signup', methods=['GET','POST'])
def signup():
    form = ContactForm(request.form)
    if request.method == 'POST':
        if form.validate ==False :
            flash('All * fields are required !')
            return render_template('signup.html',form=form)
        else:
            newuser = Entry(form.username.data , form.email.data, form.password.data, 0, 0, form.name.data, form.dob.data, 0)
            session['email'] = newuser.Email_id
            user = Entry.query.filter_by(Email_id = session['email']).first()
    
            if user is None:
                db.session.add(newuser)
                db.session.commit()
                session['logged_in'] = True
                return url_for('profile')
            else:
                flash("This email already exists, please try another !")
                return render_template('signup.html')
    elif request.method == 'GET':
        return render_template('signup.html',form=form)
    return render_template('signup.html');

@app.route('/logout')
def logout(): 
    if 'email' not in session: 
        return render_template('error.html')
    
    session['logged_in']=False
    return render_template('login.html')

@app.route('/testdb')
def testdb():
    if db.session.query("all").from_statement("SELECT username FROM entries"):
        return 'It works.'
    else:
        return 'Something is broken.'


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
