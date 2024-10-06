from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class EntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    mood = StringField('Mood', validators=[Length(max=50)])
    weather = StringField('Weather', validators=[Length(max=50)])
    location = StringField('Location', validators=[Length(max=100)])
    tags = StringField('Tags')
    submit = SubmitField('Save Entry')
