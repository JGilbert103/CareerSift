from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError
from models import user
from database import db

# Method for register form functionality
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
        submit = SubmitField('Register')

        # Checking if the email is already registered to an account
        def validateEmail(self, field):
            if db.session.query(user).filter_by(email=field.data).count() > 0:
                raise ValidationError('Email registered to another user')

        # Checking if the username is already registered to an account
        def validateUsername(self, field):
            if db.session.query(user).filter_by(username=field.data).count() > 0:
                raise ValidationError('Username is already registered to another user')

# Method for login form functionality
class LoginForm(FlaskForm):
    class Meta:
        csrf = False
        username = StringField('Username', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired()])
        submit = SubmitField('Login')

        # Validating username and password
        def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise ValidationError('Username does not exist')

    def validate_password(self, field):
        if field.data and not bcrypt.checkpw(field.data.encode('utf-8'), field.data.encode('utf-8')):
            raise ValidationError('Incorrect password')

# Method for contact us form functionality
class ContactForm(FlaskForm):
    class Meta:
        csrf = False
        # Input for email
        email = StringField('Email', [Email(message='Email is not valid'), DataRequired()])

        # Input for message/issue
        issue = StringField('Issue', validators=[length(1, 512)])

        # Form submission
        submit = SubmitField('Submit')