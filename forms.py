# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SettingsForm(FlaskForm):
    model_name = StringField('Model Name', validators=[DataRequired()])
    submit = SubmitField('Save')
