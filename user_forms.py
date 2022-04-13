from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import BooleanField, DecimalField
from wtforms.fields.simple import PasswordField
from wtforms.validators import InputRequired , DataRequired, ValidationError
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms_components import Email
from wtforms.fields.html5 import EmailField 

def my_length_check(form, field):
    if len(field.data) < 8:
        raise ValidationError('Ο κωδικός πρέπει να είναι τουλάχιστον 8 χαρακτήρες.')

class Register(FlaskForm):
    first_name = StringField('Όνομα', validators=[InputRequired()])
    last_name = StringField('Επίθετο', validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    email = EmailField('Ε-mail επικοινωνίας', validators=[DataRequired(), Email()])
    password = PasswordField("Κωδικός", validators=[InputRequired(), my_length_check])
    password_confirm = PasswordField("Επαλήθευση Κωδικού", validators=[InputRequired()])


class Login(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Κωδικός", validators=[InputRequired()])


