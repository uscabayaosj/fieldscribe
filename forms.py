from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class EntryForm(FlaskForm):
    project = StringField('Project', validators=[DataRequired(), Length(max=100)])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Length(max=100)])
    context = TextAreaField('Context')
    detailed_observation = TextAreaField('Detailed Observation', validators=[DataRequired()])
    reflection = TextAreaField('Reflection')
    tags = StringField('Tags')
    submit = SubmitField('Save Entry')
