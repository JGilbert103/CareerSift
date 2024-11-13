from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db

## Implement register form functionality
class RegisterForm(FlaskForm):
    class Meta:



## Implement login form functionality
class LoginForm(FlaskForm):
    class Meta: