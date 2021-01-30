from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField
from wtforms.validators import DataRequired, InputRequired,Length

class ArticleForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired(),Length(min=5)])
    body = TextAreaField("Content",validators=[InputRequired(),Length(min=200)])