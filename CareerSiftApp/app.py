import os 

import sqlite3
import csv
import bcrypt
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from database import db
from models import user, listing, savedListing, messages, contactMessage
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

                description = description.replace(';', ',')
                description = description.replace('~~', '\n')

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
    print(listingData)
    
    # Closing the connection to the database
    conn.close()

    return listingData



# Method to handle populating listings saved by a user
def getSaved(userid):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()
    
    # Querying the database for saved listids
    cursor.execute("""
    SELECT listid
    FROM savedListing
    WHERE userid = ?
    """, (userid,))
    savedIds = cursor.fetchall()
    
    # Flatten savedIds to get a list of listids (e.g., [1, 2, 3])
    savedIds = [x[0] for x in savedIds]  # Extracting the listid values from the tuples

    # Only proceed if there are saved listids
    if savedIds:
        # Querying the listing table using the list of listids
        cursor.execute("""
            SELECT listid, title, company, position, salary, type, sourcelink, description
            FROM listing
            WHERE listid IN ({})
        """.format(','.join('?' for _ in savedIds)), savedIds)
        
        jobs = cursor.fetchall()
        
        return jobs
    else:
        return []

    conn.close()


###   Methods to handle register, login, and logout   ###

## Method for registering a user
@app.route('/register.html', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Salting and hashing user input for password
        #shpass = bcrypt.hashpw(request.form['Password'].encode('utf-8'), bcrypt.gensalt())
        # Gathering user data entered to the application
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Create a new user object
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user WHERE username = ? OR email = ?", (username, email))
        existingUser = cursor.fetchone()

        if existingUser:
            print("existing")
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("INSERT INTO user (username, password, email, isadmin) VALUES (?, ?, ?, ?)",
                       (username, password, email, False))
        conn.commit()

        cursor.execute("SELECT userid FROM user WHERE username = ?", (username,))
        newUser = cursor.fetchone()

        conn.close()
        
        session['user'] = username
        session['userid'] = newUser[0]

        # Redirect user to home/index page
        return redirect(url_for('index'))

    if form.errors:
        print(f"Form errors: {form.errors}")
    
    # If there was an error with registering, redirect to register form
    return render_template('register.html', form=form)



## Method for logging in a user
@app.route('/login.html', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    # Validating login form on submission
    if form.validate_on_submit():
        # If form is valid, searching the databse for the matching user
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT userid, username, password, email FROM user WHERE username = ?", (form.username.data,))
        user = cursor.fetchone()

        # Checking user password
        if user and form.password.data == user[2]:
            # If the password is correct, adding the user to the session
            userid, username, password, email = user

            session['user'] = username
            session['userid'] = user[0]
            # Redirect user to home/index page
            return redirect(url_for('index'))
        
        # Redirect user to login form
        return render_template("login.html", form=LoginForm)

    # If the form did not validate
    else:
        # Redirect user to login form
        return render_template("login.html", form=LoginForm)

    if form.errors:
        print(f"Form errors: {form.errors}")



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
    # Checking if listings exist in the database before calling createListing function
    con = sqlite3.connect('CareerSiftDB.db')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(listid) FROM listing")
    row_count = cursor.fetchone()[0]
    con.close()

    # Creating listings if listing table is empty
    if row_count == 0:
        # Call the function to create listings
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
    temp = data.get('listid')
    print(type(data.get('listid')))
    listid = int(temp)

    try:
        userid = session['userid']
        ##print(f"in POST method user = ", userid)
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        print("before sql request")

        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        alreadySaved = cursor.fetchone()

        print(alreadySaved)

        if alreadySaved is not None:
            print("in isSaved conditional block")
            return jsonify({'error': 'This listing is already saved by the user'}), 407

        cursor.execute("INSERT INTO savedListing (userid, listid) VALUES (?, ?)", (userid, listid))
        
        print("executed insert")

        conn.commit()
        cursor.close()

        return jsonify({'message': 'Listing saved successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# Method for unsave listings page
@app.route('/unsaveListing', methods=['POST'])
def unsaveListing():
    data = request.json
    temp = data.get('listid')
    print(type(data.get('listid')))
    listid = int(temp)
    print(listid)

    try:
        userid = session['userid']
        print(userid)
        ##print(f"in POST method user = ", userid)
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        print("before sql request")

        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        deleteListing = cursor.fetchone()

        print("after sql request")

        print(deleteListing)

        if deleteListing is None:
            print("in deleteListing conditional block")
            return jsonify({'error': 'This listing is not saved by the user'}), 407

        print("before delete")
        cursor.execute("DELETE FROM savedListing where userid = ? AND listid = ?", (userid, listid))
        
        print("executed delete")

        conn.commit()
        cursor.close()

        return jsonify({'message': 'Listing removed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# Method for about us page
@app.route('/about.html', methods=['GET'])
def about():
    # Redirect user to about us page
    if session.get('user'):
        return render_template("about.html", user=session['user'])
    else:
        return render_template("about.html")



# Method for contact page
@app.route('/contact.html', methods=['POST','GET'])
def contact():
    form = ContactForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = request.form.get('email')
        issue = request.form.get('issue')
        #print(email, issue)

        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO contactMessage (email, issue) VALUES (?, ?)",
                            (email, issue))

        conn.commit()
        conn.close()

        return redirect(url_for('thanks'))
    
    if session.get('user'):
        return render_template("contact.html", user=session['user'], form=ContactForm)
    else:
        return render_template("contact.html")



# Method for thanks page
@app.route('/thanks.html', methods=['GET'])
def thanks():
    if session.get('user'):
        return render_template("thanks.html", user=session['user'])
    else:
        return render_template("thanks.html")



## ADD COMPARE PAGE FUNCTIONALITY
@app.route('/compare.html', methods=['GET'])
def compare():
    if session.get('user'):
        return render_template("compare.html", user=session['user'])
    else:
        return render_template("compare.html")



## ADD SAVED FUNCTIONALITY
@app.route('/saved.html', methods=['GET'])
def saved():
    # Checking which users saved listings to access
    userid = session['userid']
    print(userid)
    if not userid:
        return redirect(url_for('login'))
    
    savedJobs = getSaved(userid)

    return render_template("saved.html", user=session['user'], jobs=savedJobs)



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
@app.route('/listings/<int:listid>', methods=['GET'])
def listings(listid):
    listingData = getData(listid)

    if listingData:
        return render_template('listing.html', listing=listingData)
    else:
        return "Listing not found", 404




## Main Method
if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=True)

    
