#!/usr/bin/env python
# -*- coding: utf-8 -*-
from intro_to_flask import app
import os
from flask import Flask, render_template, session, request, flash, url_for, redirect
from Forms import ContactForm, RegistrationForm, LoginForm
from flask.ext.mail import Message, Mail
from models import db, Entry
"""from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
#from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# an Engine, which the Session will use for connection
# resources
some_engine = create_engine('postgresql://root:Internship0@localhost/')
# create a configured "Session" class
Session = sessionmaker(bind=some_engine)
# create a Session
session = Session()
#from flaskr.database import metadata"""

 
mail = Mail()
mail.init_app(app)

@app.route('/')
def home():
    #session['signed_up']=False
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  #form = LoginForm(request.form)
    form = LoginForm(request.form)
  
    if request.method == 'POST':
      if form.validate() == False:
        return render_template('login.html', form=form, session=False)
      else:
        session['email'] = form.email.data
        session['username'] = session.execute(select(username).where(Entry.c.email==[session['email']]))
        session['logged_in']=True
        return redirect(url_for('profile', success=True, session=True))
                   
    elif request.method == 'GET':
      return render_template('login.html', form=form, session=False)
  
@app.route('/signup', methods=['GET','POST'])
def signup():
    form = ContactForm(request.form)
    if request.method == 'POST':
        if form.validate() ==False :
            flash('All * fields are required !')
            return render_template('signup.html',form=form)
        else:
            form = RegistrationForm(request.form)
            return render_template('fillform.html',form=form, session=True)
    elif request.method == 'GET':
        return render_template('signup.html',form=form)
    return render_template('signup.html');

@app.route('/fillform', methods=['GET','POST'])
def fillform():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST':
        if form.validate() ==False :
            flash('All fields are required !')
            return render_template('fillform.html',form=form, session=True)
        else:
            newuser=Entry(form.username.data, form.email.data, form.password.data)
            session['email'] = newuser.email
            user = Entry.query.filter_by(email = session['email']).first()
    
        if user is None:
            db.session.add(newuser)
            db.session.commit()
            session['logged_in'] = True
            return render_template('fillform.html',form=form)
        else:
            flash("This email already exists, please try another !")
            return render_template('fillform.html')
    if request.method == 'GET':
        return render_template('fillform',form=form)
    return render_template('fillform.html', session=True)

@app.route('/logout')
def logout(): 
    if 'email' not in session: 
        return redirect(url_for('signin'))
        session.pop('email', None)
    
    session['logged_in']=False
    return render_template('home.html')

@app.route('/testdb')
def testdb():
    if db.session.query("1").from_statement("SELECT username FROM entries"):
        return 'It works.'
    else:
        return 'Something is broken.'

@app.route('/profile')
def profile():
    #if session == True:
        user = Entry.query.filter_by(email = session['email']).first()
        #flash("Hi")
        if user is None:
            flash ('User Not registered')
            return render_template('login.html')
        else:
           return render_template('profile.html')
    #else:
    #    flash("You have not yet logged in !")
    #    return render_template('login.html',form=form)


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