from flask.ext.wtf import Form
from wtforms import validators, ValidationError
from wtforms.fields import TextField, BooleanField,SubmitField, PasswordField
from wtforms.validators import Required
from models import Entry

class ContactForm(Form):
	name = TextField("Full Name*", [validators.Required("Please enter a Name")])
	email= TextField("E-mail*",[validators.Required("Please enter an e-mail address"), validators.email("Please enter a valid email address")])
	accept_tos = BooleanField('I accept the Terms Of Services', [validators.Required("Please Accept the Terms Of Services")])
	stud_co = BooleanField('Student', 'Company',[validators.Required("Please choose one of the fields")])
	mobile = TextField("Mobile (Optional)")
	city = TextField("Current City (Optional)")
	submit=SubmitField("Continue")


class RegistrationForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25,message="Username should be of minimum 4 and maximum 25 characters"),validators.Required("Please fill in a username")])
	email = TextField('Email Address', [validators.Length(min=6, max=35),validators.Required()])
	password = PasswordField('Password', [
		validators.Required("You need to type a password"),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('ReType Password',[validators.Required()])
	accept_tos = BooleanField('I accept the Terms Of Services', [validators.Required("Please Accept the Terms Of Services")])
	submit=SubmitField("Register")

	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
 
	def validate(self):
		if not Form.validate(self): 
		  return False
		user = Entry.query.filter_by(email = self.email.data.lower()).first()
		if user is None:
			return True
		else:
			self.email.errors.append("That email is already taken")
			return False

class LoginForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Log In")
   
  def __init__(self, *args, **kwargs):
	Form.__init__(self, *args, **kwargs)
 
  def validate(self):
	if not Form.validate(self):
	  return False
	 
	user = Entry.query.filter_by(email = self.email.data.lower()).first()
	if user and user.check_password(self.password.data):
	  return True
	else:
	  self.email.errors.append("Invalid e-mail or password")
	  return False
