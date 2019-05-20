from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

class AudioForm(FlaskForm):
    audio = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')