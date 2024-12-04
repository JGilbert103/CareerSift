from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email
from wtforms import ValidationError, BooleanField
from models import user
from database import db
import bcrypt

# Method for register form functionality
class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    username = StringField('Username', validators=[Length(1, 25), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmPassword', message="Passwords must match")])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired()])
    email = StringField('Email', validators=[Email(message="Invalid email address"), DataRequired()])
    notifications = BooleanField('Link email for job notifications?')
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
        username = StringField('Username', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired()])
        submit = SubmitField('Login')

       # Validating username exists in the database
        def validate_username(self, field):
            existingUser = user.query.filter_by(username=field.data).first()
            if not user:
                raise ValidationError('Username does not exist')

    # Validating password is correct
        def validate_password(self, field):
            existingUser = user.query.filter_by(username=self.username.data).first()
            if existingUser and not bcrypt.checkpw(field.data.encode('utf-8'), user.password.encode('utf-8')):
                raise ValidationError('Incorrect password')

# Method for contact us form functionality
class ContactForm(FlaskForm):
    class Meta:
        csrf = False
    # Input for email
    email = StringField('Email', validators=[Email(message='Email is not valid'), DataRequired()])
    # Input for issue
    issue = TextAreaField('Issue', validators=[DataRequired()])
    # Submit form
    submit = SubmitField('Submit')