import os 

import sqlite3
import csv
import bcrypt
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

###   Methods for site functionalities   ###

# Method to create a listing entity in the database
def createListing(dbPath, csvPath):
    # Connect to the SQLite database using the passed dbPath
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    
    try:
        # Open the CSV file and read data
        with open(csvPath, 'r') as file:  # Use csvPath here
            reader = csv.DictReader(file)
            
            # Iterate through each row in the CSV file
            for row in reader:
                # Insert listing data into the listing table
                cursor.execute('''
                    INSERT INTO listing (listid, title, company, position, salary, type, sourceLink, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['title'],
                    row['company'],
                    row['position'],
                    row['salary'],
                    row['description'],
                    row['sourceLink'],
                    row['type']
                ))
        
        # Commit the transaction
        conn.commit()
        print("Listings created successfully from CSV.")
    
    except sqlite3.Error as e:
        # Handle any database errors
        print("Error creating listings from CSV:", e)
    
    finally:
        # Close the connection
        conn.close()


# Main section to execute the function
if __name__ == "__main__":
    dbPath = '/database.db'
    csvPath = '/listings.csv'

    createListing(dbPath, csvPath)

# Method to populate job listings to home/index page
def populateListings():
    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db') ## CHANGE DATABASE FILE FORMAT ##
    cursor = conn.cursor()
    # Querying the database for listings
    cursor.execute("SELECT title, company, position, salary, type, sourcelink, description FROM listing ")
    # Saving listings found to jobs variable
    jobs = cursor.fetchall()
    # Closing connection to the database
    conn.close()
    # Returning jobs
    return jobs



###   Methods to handle register, login, and logout   ###

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
        currentUser = db.session.query(User).filter_by(username=request.form['username']).one()
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
    # Checking if user is currently signed in 
    if session.get('user'):
        # Clearing session for the user
        session.clear()

    # Redirect user to home/index page
    return redirect(url_for('index'))



###   Methods for pages   ###

# Method for home/index page
@app.route('/')
def index():
    # Calling populateListings function
    jobListings = populateListings()
    # Session verification and populating listings
    if session.get('user'):
            return render_template("index.html", user=session['user'], jobs=jobListings)
    # Populating listings
    else:
            return render_template("index.html", jobs=jobListings)

# Method for about us page
@app.route('/about', methods=['GET'])
def showAbout():
    # Redirect user to about us page
    return render_template("about.html")

## ADD CONTACT PAGE FUNCTIONALITY
@app.route('/contact', methods=[])

## ADD COMPARE PAGE FUNCTIONALITY
@app.route('/compare', methods=[])

## ADD SAVED FUNCTIONALITY
@app.route('/saved', methods=[])

## Method for settings page
@app.route('/settings', methods=['GET'])
def showSettings():
    # Checking which users settings to access
    if session.get('user'):
        # Redirect user to their settings page
        return render_template("settings.html", user=session['user'])    
    else:
        # Redirect user to settings page
        return render_template("settings.html")    



## Main Method
if __name__ == "__main__":
    app.run(debug=True)