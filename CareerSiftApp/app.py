import os 

import sqlite3
import csv
import bcrypt
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db
from models import user, listing, savedListing, messages
from forms import RegisterForm, LoginForm, ContactForm
#import jobScraper

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CareerSiftDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'
db.init_app(app)

with app.app_context():
    db.create_all()

###   Methods for site functionalities   ###

# Method to create a listing entity in the database ## NEEDS WORK ##
def createListing():
    try:
        # Open the CSV file and read data
        with open('listings.csv', 'r') as csvFile:
            reader = csv.DictReader(csvFile)
            # Iterate through each row in the CSV file
            for row in reader:
                title = row["title"].strip()
                print("title: ", title)
                company = row["company"].strip()
                #print("company:", company)
                position = row["position"].strip()
                #print("position: ", position)
                salary = row["salary"].strip()
                #print("salary:", salary)
                jobtype = row["type"].strip()
                #print("type: ", jobtype)
                sourcelink = row["sourceLink"].strip()
                #print("link: ", sourcelink)
                description = row["description"].strip()
                #print("desc: ", description)

                #print(f"Adding Listing: {title}, {company}, {position}, {salary}, {jobtype}, {sourcelink}, {description}")
                conn = sqlite3.connect('CareerSiftDB.db')
                cursor = conn.cursor()

                cursor.execute("INSERT INTO listing (title, company, position, salary, type, sourcelink, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (title, company, position, salary, jobtype, sourcelink, description))
                
                conn.commit()
            conn.close()      

    except FileNotFoundError:
        print("CSV file not found. Please ensure 'listings.csv' exists in the application directory.", "error")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating listings: {e}", "error")

# Method for removing listings (admin function) ## NEEDS WORK ##
'''
@app.route('/removeListing/<int:listid>', methods=['POST'])
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
'''

# Method to populate job listings to home/index page
def populateListings():
    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()
    # Querying the database for listings
    cursor.execute("SELECT listid, title, company, position, salary, type, sourcelink, description FROM listing ")
    # Saving listings found to jobs variable
    jobs = cursor.fetchall()
    # Closing connection to the database
    conn.close()
    # Returning jobs
    return jobs

# Method to handle populating a specific listing when clicked
def getData(listid):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()
    # Querying the database for listings
    cursor.execute("""
        SELECT listid, title, company, position, salary, type, sourcelink, description
        FROM listing
        WHERE listid = ?
    """, (listid,)) 
    
    # Fetching the listing
    listingData = cursor.fetchone()
    
    # Closing the connection to the database
    conn.close()

    return listingData

###   Methods to handle register, login, and logout   ###

## Method for registering a user
@app.route('/register.html', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Salting and hashing user input for password
        shpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # Gathering user data entered to the application
        username = request.form['username']
        email = request.form['email']
       
        # Create a new user object
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username = ? OR email = ?", (username, email))
        existingUser = cursor.fetchone()

        if existing_user:
            flash('Username or Email already taken', 'error')
            conn.close()
            return redirect(url_for('register'))
        
        cursor.execute("INSERT INTO user (username, password, email, isadmin) VALUES (?, ?, ?, ?)",
                       (username, shpass, email, False))
        conn.commit()

        cursor.execute("SELECT userid FROM user WHERE username = ?", (username,))
        newUser = cursor.fetchone()

        conn.close()
        
        session['user'] = username
        session['userid'] = newUser[0]

        # Redirect user to home/index page
        return redirect(url_for('index'))

        flash('Registration successful! Welcome to the site.', 'success')
        return redirect(url_for('index'))
    
    # If there was an error with registering, redirect to register form
    return render_template('register.html', form=form)

## Method for logging in a user
@app.route('/login.html', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    # Validating login form on submission
    if form.validate_on_submit():
        # If form is valid, searching the databse for the matching user
        user = db.session.query(user).filter_by(username=form.username.data).first()
        # Checking user password
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')):
            # If the password is correct, adding the user to the session
            session['user'] = user.username
            session['userid'] = user.userid
            # Redirect user to home/index page
            return redirect(url_for('index'))
        
        # If the password was incorrect, send error message
        form.password.errors.append = ["Incorrect username or password"]
        # Redirect user to login form
        return render_template("login.html", form=LoginForm)

    # If the form did not validate
    else:
        # Redirect user to login form
        return render_template("login.html", form=LoginForm)

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
    createListing()
    # Calling populateListings function
    jobListings = populateListings()
    # Session verification and populating listings
    if session.get('user'):
            return render_template("index.html", user=session['user'], jobs=jobListings)
    # Populating listings
    else:
            return render_template("index.html", jobs=jobListings)

# Method for save listings page
@app.route('/saveListing', methods=['POST'])
def saveListing():
    # Recieve the incoming json data from front end
    data = request.json
    # Saving the listid for the saved listing
    listid = data.get('listid')
    # Saving the userid for the saved listing
    userid = session.get('userid')
    # Handling error if the user is not logged in
    if not userid:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        # Check if the listing is already saved by this user
        existingListing = savedListing.query.filter_by(userid=userid, listid=listid).first()
        if existingListing:
            return jsonify({'error': 'This listing is already saved by the user'}), 400

        # Create a new saved listing record
        newListing = savedListing(userid=userid, listid=listid)

        # Add the new saved listing to the session and commit it to the database
        db.session.add(newListing)
        db.session.commit()

        return jsonify({'message': 'Listing saved successfully'}), 200  # Success response

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500  # Handle other errors

# Method for unsave listings page
@app.route('/unsaveListing', methods=['POST'])
def unsaveListing():
    data = request.json
    listid = data.get('listid')
    userid = session.get('userid')

    if not userid:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        # Find the saved listing entry to delete
        exsistingSavedListing = savedListing.query.filter_by(userid=userid, listid=listid).first()

        # If the saved listing doesn't exist, return an error
        if not exsistingSavedListing:
            return jsonify({'error': 'This listing is not saved by the user'}), 400

        # Delete the saved listing
        db.session.delete(exsistingSavedListing)

        # Commit the transaction
        db.session.commit()

        return jsonify({'message': 'Listing unsaved successfully'}), 200  # Success response

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500  # Handle other errors

# Method for about us page
@app.route('/about.html', methods=['GET'])
def about():
    # Redirect user to about us page
    return render_template("about.html")

## ADD CONTACT PAGE FUNCTIONALITY
@app.route('/contact.html', methods=['GET'])
def contact():
    form = ContactForm()

    if request.method == 'POST' and form.validate_on_submit():
        '''
        # Save the contact form message to the database (or process as needed)
        contact_message = ContactMessage(
            email=form.email.data,
            issue=form.issue.data
        )

        # Save the contact message to the database
        db.session.add(contact_message)
        db.session.commit()

        # Flash a success message
        flash('Your message has been sent!', 'success')
        
        return redirect(url_for('contact'))  # Redirect to the contact page after submission
        '''

    return render_template('contact.html', form=ContactForm)

## ADD COMPARE PAGE FUNCTIONALITY
@app.route('/compare', methods=[])

## ADD SAVED FUNCTIONALITY
@app.route('/saved', methods=[])

# Method for settings page
@app.route('/settings.html', methods=['GET'])
def settings():
    # Checking which users settings to access
    if session.get('user'):
        # Redirect user to their settings page
        return render_template("settings.html", user=session['user'])    
    else:
        # Redirect user to settings page
        return render_template("settings.html")    

# Method for listing page
@app.route('/listing/<int:listid>', methods=['GET'])
def listing(listid):
    listingData = getData(listid)

    if listingData:
        return render_template('listing.html', listing=listingData)
    else:
        return "Listing not found", 404




## Main Method
if __name__ == '__main__':

    # Start the Flask application
    app.run(debug=True)
