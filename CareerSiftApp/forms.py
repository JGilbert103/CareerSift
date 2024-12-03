from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import User
from database import db

## Implement register form functionality
class RegisterForm(FlaskForm):
    class Meta:
        csrf = False
        # Input for username
        username = StringField('Username', validators=[Length(1, 25)])

        # Input for password
        password = PasswordField('Password', [DataRequired(message="Enter a password to create an account"),
        EqualTo('confirmPassword', message="Passwords entered must match")])

        # Input for confirm password
        confirmPassword = PasswordField('Confirm Password', validators=[Length(min=10, max=25)])

        # Input for email
        email = StringField('Email',[Email(message='Email is not valid'), DataRequired()])

        # Form submission
        submit = SubmitField('Submit')

        # Checking if the email is already registered to an account
        def validateEmail(self, field):
            if db.session.query(user).filter_by(email=field.data).count() != 0:
                raise ValidationError('Email registered to another user')


## Implement login form functionality
class LoginForm(FlaskForm):
    class Meta: