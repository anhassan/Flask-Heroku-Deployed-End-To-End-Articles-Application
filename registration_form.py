from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField("Name",validators=[InputRequired()])
    email = StringField("Email",validators=[InputRequired(),Length(min=8,max=16)])
    username = StringField("Username", validators=[InputRequired(),Length(min=6,max=12)])
    password = PasswordField("Password",validators=[InputRequired(),Length(min=8,max=12),
                                                  EqualTo("confirm",message="Passwords should match")])
    confirm = PasswordField("Confirm Password ",validators=[InputRequired(),Length(min=8,max=12)])


