from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username",validators=[InputRequired(),Length(min=6,max=12)])
    password = PasswordField("Password",validators=[InputRequired(),Length(min=6,max=12)])

