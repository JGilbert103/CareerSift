import os 

# import bcrypt
from flask import Flask, redirect, url_for, render_template, request, session
from database import db
from models import User as User
from models import Listing as listing
from models import SavedListing as SavedListing
from models import Messages as Messages
from forms import RegisterForm, LoginForm
import jobScraper

app = Flask(__name__)

# ADD APP CONFIGS

## Method for session verification
@app.route('/')
def index():
        if session.get('user'):
                return render_template("index.html", user=session['user'])

        else:
                return render_template("index.html")

## Method for registering a user
@app.route('/register', methods=['POST', 'GET'])
def register();
    regForm = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Salting and hashing user input for password
        shpass = bcrypt.hashpw(request.form['password'].encode('utf=8'), bcrypt.gensalt())

        # Gathering user data entered to the application
        username = request.form['username']

        # Create a new user model
        nUser = User(username, shpass, request.form['email'], isadmin)

        # Add gathered data to the database for a new user
        db.session.add(newUser)
        db.session.commit()

        # Saving the users session
        session['newUser'] = username
        # Generating a userid for the user
        session['userid'] = newUser.userid 

        # Redirect user to home/index page
        return redirect(url_for('index'))
    
    # If there was an error with registering, redirect to register form
    return render_template('register.html', form=form)

## Method for logging in a user
@app.route('/login', methods=['POST', 'GET'])
def login():
    logForm = LoginForm()
    # Validating login form on submission
    if logForm.validate_on_submit():
        # If form is valid, searching the databse for the matching user
        currentUser = db.session.query(User).filter_by(email=request.form['email']).one()
        # Checking user password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), currentUser.password):
            # If the password is correct, adding the user to the session
            session['user'] = currentUser.username
            session['userid'] = currentUser.userid
            # Redirect user to home/index page
            return redirect(url_for('index'))
        
        # If the password was incorrect, send error message
        logForm.password.errors = ["Incorrect username or password"]
        # Redirect user to login form
        return render_template("login.html", form=logForm)

    # If the form did not validate
    else:
        # Redirect user to login form
        return render_template("login.html" form=logForm)


## Logging out a user
@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

## ADD ABOUT PAGE FUNCTIONALITY

## ADD CONTACT PAGE FUNCTIONALITY

## ADD COMPARE PAGE FUNCTIONALITY

## ADD LISTING FUNCTIONALITY

## ADD SETTINGS FUNCTIONALITY



## Main Method
if __name__ == "__main__":
    app.run()