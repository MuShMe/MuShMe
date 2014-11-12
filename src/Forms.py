from flask.ext.wtf import Form
from wtforms import validators, ValidationError
from wtforms.fields import TextField, BooleanField,SubmitField, PasswordField, DateField, SelectField, TextAreaField, RadioField, FileField
from wtforms.validators import Required
from wtforms.widgets.core import Select, HTMLString, html_params

class SelectDateWidget(object):
    FORMAT_CHOICES = {
        '%d': [(x, str(x)) for x in range(1, 32)],
        '%m': [(x, str(x)) for x in range(1, 13)],
        '%y': [(x, str(x)) for x in range(1950, 2014)],
    }

    def __call__(self, field, **kwargs):
        field_id = kwargs.pop('id', field.id)
        html = []
        for format in field.format.split():
            choices = self.FORMAT_CHOICES[format]
            id_suffix = format.replace('%', '-')
            params = dict(kwargs, name=field.name, id=field_id + id_suffix)
            html.append('<select %s>' % html_params())
            if field.data:
                current_value = int(field.data.strftime(format))
            else:
                current_value = None
            for value, label in choices:
                selected = (value == current_value)
                html.append(Select.render_option(value, label, selected))
            html.append('</select>')

        return HTMLString(''.join(html))

class ContactForm(Form):
	name = TextField("Full Name", [validators.Required("Please enter a Name")])
	username = TextField('Username', [validators.Length(min=4, max=25,message="Username should be of minimum 4 and maximum 25 characters"),validators.Required("Please fill in a username")])
	email = TextField('Email Address', [validators.Length(min=6, max=35),validators.Required()])
	password = PasswordField('Password', [
		validators.Required("You need to type a password"),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Confirm Password',[validators.Required("Please Enter your Date Of Birth")])
	accept_tos = BooleanField('I accept the Terms Of Services', [validators.Required("Please Accept the Terms Of Services")])

class LoginForm(Form):
	email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
	password = PasswordField('Password', [validators.Required("Please enter a password.")])

class AddPlaylist(Form):
    add = TextField()


#class AddSong(Form):

class ReportForm(Form):
    report = RadioField('What do we report ?',choices=[('Vulgarity','It contains Vulgarity'),('spam',"It's Spam"),('Other','Other')])
    other = TextAreaField("Other ??")

#class AddPlaylist(Form):

class editForm(Form):
    name = TextField("Full Name",[validators.Required()])
    dob = DateField(format='%d %m %y', widget=SelectDateWidget() )
    pic = FileField('Upload Picture')

class CommentForm(Form):
    comment = TextAreaField("Add Comment ... ")

class searchForm(Form):
    entry = TextField("Search")
