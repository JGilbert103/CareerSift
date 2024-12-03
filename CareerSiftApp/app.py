import os 

import sqlite3
import csv
import bcrypt
from flask import Flask, redirect, url_for, render_template, request, session
from database import db
from models import user as user
from models import listing as listing
from models import savedListing as savedListing
from models import messages as messages
from forms import RegisterForm, LoginForm
import jobScraper

app = Flask(__name__)

# ADD APP CONFIGS

###   Methods for site functionalities   ###

# Method to create a listing entity in the database ## NEEDS WORK ##
def createListing():
    # Path to CSV file
    csvPath = os.path.join(os.path.dirname(__file__), 'listings.csv')
    
    try:
        # Open the CSV file and read data
        with open(csvPath, 'r') as csvFile:
            reader = csv.DictReader(csvFile)
            
            # Iterate through each row in the CSV file
            for row in reader:
                # Insert listing data into the listing table
                newListing = listing(
                    title=row.get('title', '').strip(),
                    company=row.get('company', '').strip(),
                    position=row.get('position', '').strip(),
                    salary=row.get('salary', '').strip(),
                    type=row.get('type', '').strip(),
                    sourceLink=row.get('sourceLink', '').strip(),
                    description=row.get('description', '').strip(),
                )
                # Add listing to the database
                db.session.add(newListing)

            # Commit changes to the database
            db.session.commit()

        except FileNotFoundError:
            flash("CSV file not found. Please ensure 'listings.csv' exists in the application directory.", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating listings: {e}", "error")


# Method for removing listings (admin function) ## NEEDS WORK ##
#@app.route('/removeListing/<int:listid>', methods=['POST'])
def removeListing(listid):
     if 'user' not in session or not session.get('isadmin'):
        # Restrict access to admins only
        flash("Unauthorized access. Admins only.", "error")
        return redirect(url_for('index'))

    try:
        # Query the listing by listid
        listing = Listing.query.get(listid)

        if listing:
            # Remove the listing
            db.session.delete(listing)
            db.session.commit()
            flash(f"Listing ID {listid} removed successfully.", "success")
        else:
            flash(f"Listing ID {listid} not found.", "warning")
    except Exception as e:
        # Handle database errors
        db.session.rollback()
        flash(f"Error removing listing: {e}", "error")
    
    return redirect(url_for('admins'))





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
def register():
    regForm = RegisterForm()

    if request.method == 'POST' and regForm.validate_on_submit():
        # Salting and hashing user input for password
        shpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())

        # Gathering user data entered to the application
        username = request.form['username']

        # Create a new user model
        newUser = user(username, shpass, request.form['email'])

        # Add gathered data to the database for a new user
        db.session.add(newUser)
        db.session.commit()

        # Saving the users session
        session['user'] = username
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
if __name__ == '__main__':
    from app import app
    with app.app_context():
        # Run the createListing function
        createListing()

    # Start the Flask application
    app.run(debug=True)
