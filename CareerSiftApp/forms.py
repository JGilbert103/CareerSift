'''
ABOUT
Author: Owen Hartzell 801188721 ohartzel@charlotte.edu
For: ITSC 3155, Software Engineering, Fall 2024
Project: Final Project - Group 9, "CareerSift"
'''

## Imports ##
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import Length, Regexp, DataRequired, EqualTo, Email, Optional
from wtforms import ValidationError, BooleanField
from models import user
from database import db



# Class for register form
class RegisterForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    # Form fields for user registration
    username = StringField('Username', validators=[Length(1, 25), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmPassword', message="Passwords must match")])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email(message="Invalid email address")])
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



# Class for login form
class LoginForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    # Form fields for user login
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



# Class for contact form
class ContactForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    # Form fields for contacting the CareerSift team
    email = StringField('Email', validators=[Email(message='Email is not valid'), DataRequired()])
    issue = TextAreaField('Issue', validators=[DataRequired()])
    submit = SubmitField('Submit')



# Class for personal info form
class PersonalInfoForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    # Form fields for updating personal info
    username = StringField('username', validators=[Optional()])
    profilePic = FileField('Profile Picture', validators=[Optional()])
    submit = SubmitField('Save Changes')



# Class for change password form
class ChangePasswordForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    # Form fields for changing password
    currentPassword = PasswordField('currentPassword', validators=[DataRequired()])
    newPassword = PasswordField('newPassword', validators=[DataRequired(), EqualTo('confirmPassword', message="Passwords must match")])
    confirmPassword = PasswordField('confirmPassword', validators=[DataRequired()])
    submit = SubmitField('Change Password')



# Class for delete account form
class DeleteAccountForm(FlaskForm):
    class Meta:
        # Disable CSRF protection (NOT FOR PRODUCTION USE)
        csrf = False

    #Form fields for deleting account
    submit = SubmitField('Delete Account')
