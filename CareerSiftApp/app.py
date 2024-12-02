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

## Session verification
@app.route('/')
def index():
        if session.get('user'):
                return render_template("index.html", user=session['user'])

        else:
                return render_template("index.html")

## ADD REGISTER METHOD
@app.route('/register', methods=['POST', 'GET'])
def register();
    form = RegisterForm()

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
        session['nUser'] = username
        # Generating a userid for the user
        session['userid'] = new_user.id 

        # Redirect user to home/index page
        return redirect(url_for('index'))
    
    # If there was an error with registering, redirect to register form
    return render_template('register.html', form=form)

## ADD LOGIN METHOD

## Logging out a user
@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))

## IMPLEMENT ADDITIONAL NEEDED METHODS BELOW



## Main Method
if __name__ == "__main__":
    app.run()