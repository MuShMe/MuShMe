from flask import Flask
import os
from werkzeug import secure_filename
 
app = Flask(__name__)

UPLOAD_FOLDER = "{{ url_for('static','img/ProfilePic') }}"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



app.secret_key = 'maximumdamage'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'mushmemusic@gmail.com'
app.config["MAIL_PASSWORD"] = 'music@mushme'
app.config['DEFAULT_MAIL_SENDER'] = 'mushmemusic@gmail.com'


app.config.from_envvar('FLASKR_SETTINGS', silent=True)
 
from mushme import mail
mail.init_app(app)

import src.mushme