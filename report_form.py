from flask_wtf import FlaskForm
from wtforms.fields.simple import  TextAreaField
from wtforms.validators import  InputRequired 


class ReportForm(FlaskForm):
    description = TextAreaField('Γιατί επιθυμείτε να αναφέρετε την συγκεκριμένη αγγελία;', validators=[InputRequired()])