from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.core import SelectField, SelectMultipleField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Email 
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields.html5 import EmailField 


class Animal_Aggelia(FlaskForm): 
    photo = FileField("Φωτογραφία (μεχρι 1mb)", validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Images only!")])
    name = StringField('Ονοματεπώνυμο (προαιρετικό)')
    email = EmailField('Ε-mail επικοινωνίας', validators=[DataRequired(), Email()])
    species = SelectField('Είδος Κατοικιδίου', choices=[("dog", "dog"), ("cat","cat"), ("other", "other")], validators=[InputRequired()])
    where_lost = StringField('Που Χάθηκε', validators=[InputRequired()])
    when_lost = StringField('Πότε Χάθηκε (προαιρετικό)')
    contact_number = StringField('Τηλέφωνο Επικοινωνίας (προαιρετικό)')
    description = TextAreaField('Λεπτομέρειες')


class Hospitality_Aggelia(FlaskForm):
    name = StringField('Ονοματεπώνυμο (προαιρετικό)')
    species = SelectMultipleField('Μπορω να φιλοξενήσω (μπορείτε να επιλεξετε πανω απο 1)', choices=[("dog", "dog"), ("cat","cat"), ("other", "other")], validators=[InputRequired()])
    email = EmailField('Ε-mail επικοινωνίας', validators=[DataRequired(), Email()])
    address = StringField('Διεύθυνση (προαιρετικό)')
    contact_number = StringField('Τηλέφωνο Επικοινωνίας (προαιρετικό)')
    description = TextAreaField('Λεπτομέρειες')