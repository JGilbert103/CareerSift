'''
ABOUT
Author: Owen Hartzell 801188721 ohartzel@charlotte.edu
For: ITSC 3155, Software Engineering, Fall 2024
Project: Final Project - Group 9, "CareerSift"
'''

## Imports ##
import os 

import sqlite3
import csv
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from database import db
from models import user, listing, savedListing, messages, contactMessage
from forms import RegisterForm, LoginForm, ContactForm, PersonalInfoForm, ChangePasswordForm, DeleteAccountForm
from werkzeug.utils import secure_filename
#import jobScraper

# Setting path for folder to save uploaded user profile picture images
UPLOAD_FOLDER = 'static/profilepics'
# Setting allowed file types for user uploaded profile pictures
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

## Initalize Flask application ##
app = Flask(__name__)

## App configs ##
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CareerSiftDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db.init_app(app)

## Creating database tables ##
with app.app_context():
    db.create_all()



## App routes ##

@app.route('/register.html', methods=['POST', 'GET'])
def register():
    '''
    Handles the user registration process

    - If the user is already logged in, redirects to index page
    - Displays a registration form and processes the form submission
    - Validates input data and checks for duplicate accounts (username and/or email)
    - Inserts a new user into the database if the validation process is
      successful and redirects to the index page
    
    Returns:
        If GET or unsuccessful POST request: Renders the registration form
        If successful POST request: Redirects to the index page
    '''

    # Checking if the user is already logged in, redirects to index page if true
    if session.get('user'):
        return redirect(url_for('index'))

    # If the user is not logged in
    else:
        # Instantiate the register form
        form = RegisterForm()
        # If the request is post and the form is valid on submission
        if request.method == 'POST' and form.validate_on_submit():

            # Gathering user data entered to the application
            username = form.username.data
            email = form.email.data.strip() if form.email.data else None
            password = form.password.data

            # Connecting to the database
            conn = sqlite3.connect('CareerSiftDB.db')
            cursor = conn.cursor()

            # Querying the database for username to check if the username already exists
            cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
            existingUsername = cursor.fetchone()

            # If the username already exists in the database, redirect to register page
            if existingUsername is not None:
                flash('Account already exisits with given username', 'error')
                # Close connection to database
                conn.close()
                return redirect(url_for('register'))
            
            # If the user entered an email address for their account
            if email is not None:
                # Querying the database for email to check if the email already exists 
                cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
                existingEmail = cursor.fetchone()

                # If the email already exists in the database, redirect to register page
                if existingEmail is not None:
                    flash('Account already exisits with given email', 'error')
                    # Close connection to database
                    conn.close()
                    return redirect(url_for('register'))

            # If the username and email dont already exist, query the database to insert a new user
                # Inserts the values username, password, and email for the new user
            cursor.execute("INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                        (username, password, email,))
            conn.commit()

            # Querying the database for attributes of the newly created user to start a new session
            cursor.execute("SELECT userid, username, password, email, profilepic FROM user WHERE username = ?", (username,))
            user = cursor.fetchone()
            # Close connection to database
            conn.close()
            
            # Creating a new session for the user
            session['user'] = username
            session['userid'] = user[0]
            session['profilepic'] = user[4]

            # Redirect user to home/index page
            return redirect(url_for('index'))
    
    # If there was an error with registering, redirect to register form
    return render_template('register.html', form=form)



@app.route('/login.html', methods=['POST', 'GET'])
def login():
    '''
    Handles user login process

    - If the user is already logged in, redirects to the index page
    - Displays a login form and processes the form submission
    - Validates the submitted form, checks inputted username and password against the database
    - Creates a session for the user upon successful authentication

    Returns:
        If GET request or unsuccessful POST request: Renders the login form again
        If successful POST request: Redirects to index page
    '''

    # Checking if the user is already logged in, redirects to index page if true
    if session.get('user'):
        return redirect(url_for('index'))

    # If the user is not logged in
    else:
        # Instantiating the login form
        form = LoginForm()
        # If the form is valid on submit
        if form.validate_on_submit():
            # Connecting to the database
            conn = sqlite3.connect('CareerSiftDB.db')
            cursor = conn.cursor()
            
            # Querying the database for a matching user
            cursor.execute("SELECT userid, username, password, email, profilepic FROM user WHERE username = ?", (form.username.data,))
            user = cursor.fetchone()

            # Checking user password
            if user and form.password.data == user[2]:
                # If the password is correct, adding the user to the session
                userid, username, password, email, profilepic = user

                # Creating a new session for the user
                session['user'] = username
                session['userid'] = user[0]
                session['profilepic'] = user[4]

                # Redirect user to home/index page
                return redirect(url_for('index'))
            
            # Redirect user to login form
            flash('Invalid username or password', 'error')
            return render_template("login.html", form=LoginForm)

    # If the form did not validate
    return render_template("login.html", form=LoginForm)



@app.route('/logout')
def logout():
    '''
    Handles the user logout process

    - Checks if the user is currently logged in
    - Clears the users session data to log them out
    - Redirects the user to the index page

    Returns:
        Redirect to the index page
    '''

    # Checking if user is currently signed in 
    if session.get('user'):
        # Clearing session for the user
        session.clear()

    # Redirect user to home/index page
    return redirect(url_for('index'))



@app.route('/')
def index():
    '''
    Handles requests to the index page
    - Processes search parameters for job listings
    - Populates the listing table by calling the createListing function
    - Retrieves job listings based on search parameters by calling the populateListings function
    - If the user is logged in, retrieves and passes their saved listings
    - Currently populates database only if it is empty for proof of concept

    Returns:
        Renders the index page with job listings and user specific data
    '''

    # Retrieving optional search parameters from teh URL
    searchTerm = request.args.get('search', '').strip()
    jobType = request.args.getlist('jobType')
    position = request.args.getlist('position')

    # Connecting to the database
    con = sqlite3.connect('CareerSiftDB.db')
    cursor = con.cursor()
    # Querying the database for job listings
    cursor.execute("SELECT COUNT(listid) FROM listing")
    row_count = cursor.fetchone()[0]
    con.close()

    # Creating listings if listing table is empty by calling createListings
    if row_count == 0:
        createListing()

    # Populating listings by calling populateListings with the optional search parameters
    jobListings = populateListings(searchTerm, jobType, position)

    # Checking if the user is logged in
    if session.get('user'):
        # Connecting to the database
        con = sqlite3.connect('CareerSiftDB.db')
        cursor = con.cursor()
        # Retreiving the current users userid from the session data
        userid = session['userid']
        # Querying the database to retreive the users saved listings 
        cursor.execute("SELECT listid FROM savedListing WHERE userid = ?", (userid,))
        userSavedListings = cursor.fetchall()
        userSavedListings = [x[0] for x in userSavedListings]
        
        # Close connection to database
        con.close()
        # Render the index page with user and job listing data
        return render_template("index.html", user=session['user'], jobs=jobListings, saved=userSavedListings)
    # If the user is not logged in, render the index page with all job listings
    else:
        return render_template("index.html", jobs=jobListings)



@app.route('/saveListing', methods=['POST'])
def saveListing():
    '''
    Handles requests to save a job listing for the logged in user

    - Receives listid from the frontend via JSON
    - Checks if the listing is already saved by the user
    - If not, inserts the listing into the savedListing table
    - Returns appropriate JSON requests for success or error

    Returns:
        JSON response indicating success or failure
    '''

    # Recieve the incoming JSON data from front end
    data = request.json
    temp = data.get('listid')
    listid = int(temp)

    try:
        # Retrieve the userid from the session
        userid = session['userid']

        # Connecting to the database
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        # Querying the database to see if the given listing is already saved by the user
        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        alreadySaved = cursor.fetchone()

        # If the listing is already saved, return an error
        if alreadySaved is not None:
            return jsonify({'error': 'This listing is already saved by the user'}), 407

        # If the listign is not saved, insert the listing into the savedListing table
        cursor.execute("INSERT INTO savedListing (userid, listid) VALUES (?, ?)", (userid, listid))
        conn.commit()
        # Close connection to database
        cursor.close()
        # Return success
        return jsonify({'message': 'Listing saved successfully'}), 200

    # Exception handling
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/unsaveListing', methods=['POST'])
def unsaveListing():
    '''
    Handles requests to unsave a job listing for the logged in user

    - Receives listid from the frontend via JSON
    - Checks if the listing is saved by the user
    - If saved, removes the listing from the savedListing table
    - Returns appropriate JSON responses for success or error

    Returns:
        JSON response indicating success or failure
    '''

    # Receive the incoming JSON data from front end
    data = request.json
    temp = data.get('listid')
    listid = int(temp)

    try:
        # Retrieve the userid from the session
        userid = session['userid']
        # Connecting to the database
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        # Querying the database to seeif the given listing is saved
        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        deleteListing = cursor.fetchone()

        # If the listing is not saved, return an error
        if deleteListing is None:
            return jsonify({'error': 'This listing is not saved by the user'}), 407

        # If the listing is saved, querying the database to delete the listing
        cursor.execute("DELETE FROM savedListing where userid = ? AND listid = ?", (userid, listid))
        conn.commit()
        # Close connection to database
        cursor.close()
        # Return success
        return jsonify({'message': 'Listing removed successfully'}), 200
    # Exception handling
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/about.html', methods=['GET'])
def about():
    '''
    Renders the about page

    - If the user is logged in, template is rendered with user data
    - If the user is not logged in, template is rendered without user data

    Returns:
        Rendered about template with or without user data
    '''

    # If the user is logged in, render about page with user data
    if session.get('user'):
        return render_template("about.html", user=session['user'])
    # If the user is not logged in, render the about page without user data
    else:
        return render_template("about.html")



@app.route('/contact.html', methods=['POST','GET'])
def contact():
    '''
    Handles the contact form submission and renders contact page

    - If the form is submitted, the users message is saved
    - If the form is not submitted or the user is logged out, the contact page is rendered

    Returns:
        Redirect to thanks page after successful form submission or renders the contact page
    '''

    # Instantiate the contact form
    form = ContactForm()

    # If the request is POST and the form is valid on submit
    if request.method == 'POST' and form.validate_on_submit():
        # Retreive the form data for email and issue
        email = request.form.get('email')
        issue = request.form.get('issue')

        # Connecting to the database
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()
        # Querying the database to save the message
        cursor.execute("INSERT INTO contactMessage (email, issue) VALUES (?, ?)",
                            (email, issue))
        conn.commit()
        # Close connection to database
        conn.close()
        # Redirecting the user to thanks page
        return redirect(url_for('thanks'))

    # If the user is logged in, renders the contact page with user data
    if session.get('user'):
        return render_template("contact.html", user=session['user'], form=ContactForm)
    # If the user is not logged in, renders the contact page without user data
    else:
        return render_template("contact.html")



@app.route('/thanks.html', methods=['GET'])
def thanks():
    '''
    Renders the thanks page to show confirmation after contact form submission

    - If the user is logged in, renders page with user data
    - If the user is not logged in, renders page without user data

    Returns:
        Render the thanks page with or without user data
    '''

    # If the user is logged in, renders the thanks page with user data
    if session.get('user'):
        return render_template("thanks.html", user=session['user'])
    # If the user is not logged in, renders the thanks page without user data
    else:
        return render_template("thanks.html")



@app.route('/compare', methods=['POST','GET'])
def compare():
    '''
    Handles comparing listings based on selected job listings

    - If the user is logged in, retreives selected job listings and calls compareJobs function
    - If the user is not logged in, renders login page

    Returns:
        If the user is logged in, renders the compare page with job comparison results
        If the user is not logged in, redirects to the login page
    '''

    # Retrieve the listids of selected jobs to be compared
    listids = request.args.getlist('compare')

    # If the user is logged in, retrieve userid from session and call compareJobs function with listids
    if session.get('user'):
        userid = session['userid']
        comparedJobs = compareJobs(listids)
        # Render compare page with user data and listing data
        return render_template("compare.html", user=session['user'], jobs=comparedJobs)
    
    # If the user is not logged in, redirect to the login page
    else:
        return redirect(url_for('login'))



@app.route('/saved.html', methods=['GET'])
def saved():
    '''
    Displays the saved job listings for the current user

    Retreives a users saved jobs based on their userid and handles adding search filters

    Returns:
        If a user is logged in, renders saved page with user data
        If a user is not logged in, redirects to the login page
    '''

    # Checking if the user is logged in
    if session.get('user'):
        # Retrieve the userid from the session
        userid = session['userid']
        # Retrieve any search filters added to the request
        savedSearchQuery = request.args.get('search', '').strip()
        jobType = request.args.getlist('jobType')
        position = request.args.getlist('position')
        # Callling the getSaved function with optional search filters to populate saved listings
        savedJobs = getSaved(userid, savedSearchQuery, jobType, position)

        # Rendering the saved page with user and saved listing data
        return render_template("saved.html", user=session['user'], jobs=savedJobs)

    # If the user is not logged in, redirect to the login page
    return redirect(url_for('login'))



@app.route('/savedlisting/<int:listid>')
def savedlisting(listid):
    '''
    Displays the details of a specific saved listing based on listid

    This function retrieves attributes for a sepcific listing based on the provided listid
    and displays that listing to the user. If the user is logged in, user data is passed.
    If the user is not logged in, redirects to login page.

    Args:
        listid (int): The listid of the given job listing

    Returns:
        Rendered saved listing if the listing exists, error if not
    '''

    # Retrieve the job listing attributes based on the given listid
    listingData = getData(listid)

    # If the listing exists, render the page with appropriate data
    if listingData:
        # Checking if the user is logged in
        if session.get('user'):
            # Render page with user and listing data
            return render_template('savedlisting.html', user=session['user'], listing=listingData)
        else:
            # If the user is not logged in, redirect to login page
            return redirect(url_for('login'))
    # If the listing does not exist, return error
    else:
        return "Listing not found", 404



@app.route('/settings.html', methods=['POST','GET'])
def settings():
    '''
    Handles functionality of the settings page, allows user to manage aspects of their account.
    Allows users to change username, profile picture, password, and delete account

    Handles GET and POST requests to render settings page and process form submissions

    Returns:
        If the user is logged in, renders settings page with forms for account management
        If the user is not logged in, redirects to the login page
    '''

    # Checking if a user is logged in 
    if session.get('user'):
        # Instantiating forms on the settings page
        personalInfoForm = PersonalInfoForm()
        changePasswordForm = ChangePasswordForm()
        deleteAccountForm = DeleteAccountForm()

        # If the request is POST
        if request.method == 'POST':
            # Retrieve the userid from the session
            userid = session['userid']
            # Retreive the form type from the POST request
            formType = request.form.get('form')

            # If the form is the personal info form and the form is valid on submission
            if formType == 'PersonalInfoForm' and personalInfoForm.validate_on_submit():
                # Retrieve the username and or profile pic from the form
                username = personalInfoForm.username.data
                profilePic = personalInfoForm.profilePic.data

                # If neither fields are provided, redirect to settings page
                if username is None and profilePic is None:
                    #flash("Please provide a new username or upload a profile picture.", "personal-info-error")
                    return redirect(url_for('settings'))
                
                # Handling username change
                try:
                    # If a username is provided, call the updatePersonalInfo fuction with userid and new username
                    if username:
                        updatePersonalInfo(userid, username=username)
                        #flash("Personal Information updated successfully!", "personal-info-success")

                # Exception handling
                except Exception as e:
                    flash(f"An error occurred: {e}", "danger")

                # Handling profile picture chagne
                try:
                    # If a profile picture is provided, and the file type is alloed
                    if profilePic and allowedFile(profilePic.filename):
                        # Retrieve secure file name
                        filename = secure_filename(profilePic.filename)
                        # Generating a new file name with the userid
                        newFilename = f"user_{userid}_{filename}"
                        # Setting the path for the new file 
                        profilePath = os.path.join(app.config['UPLOAD_FOLDER'], newFilename)
                        # Saving the file path
                        profilePic.save(profilePath)
                        # Generating the url for the new profile picture
                        profilePicUrl = f"/static/profilepics/{newFilename}"
                        # Calling the updatePersonalInfo function with userid and generated profile picture file path
                        updatePersonalInfo(userid, profilePic=profilePicUrl)
                
                # Exception handling
                except Exception as e:
                    flash(f"An error occurred: {e}", "danger")
                
                #flash("Please provide a new username or upload a profile picture.", "personal-info-error")
                return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm) 

            # If the form type is change password form and the form is valid on submission
            elif formType == 'ChangePasswordForm' and changePasswordForm.validate_on_submit():
                # Retrieve the current and new passwords from the form
                currentPassword = changePasswordForm.currentPassword.data
                newPassword = changePasswordForm.newPassword.data
                
                # Handling password change
                try:
                    # Retrieve the password stored in the database for the user by calling getPassword with userid
                    storedPassword = getPassword(userid)

                    # If the password entered does not match the one stored in the database, throw error and render settings page
                    if storedPassword != currentPassword:
                        flash('Invalid current password', 'error')
                        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm) 

                    # Update users password by calling updatePassword function with userid and new password
                    updatePassword(userid, newPassword)

                # Exception handling
                except Exception as e:
                    #flash(f"An error occurred: {e}", "danger")
                    return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)

            # If the form type is delete account form and the form is valid on submission
            elif formType == 'DeleteAccountForm' and deleteAccountForm.validate_on_submit():
                # Handling delete account
                try:
                    # Calling delete account function with userid and redirecting to logout to clear the session
                    deleteUser(userid)
                    return redirect(url_for('logout'))

                # Exception handling
                except Exception as e:
                    #flash(f"An error occurred: {e}", "danger")
                    return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)


        # Redirect user to their settings page
        #flash('Invalid current password', 'error')
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)    
    else:
        # Redirect user to login page
        return redirect(url_for('login'))   



@app.route('/listings/<int:listid>', methods=['GET'])
def listings(listid):
    '''
    Renders the listing page for a sepcific listing based on provided listid, if the listing exists, 
    renders the page with listing data. If the user is logged in, user data is rendered as well. If 
    the user is not logged in, user data will not be rendered

    Args:
        listid (int): The listid of the listing

    Returns:
        If the listing exists, renders the page with listing data and renders without user data
        If the listing does not exsist, error
    '''

    # Calling getData based on listid to retrieve attributes for a listing
    listingData = getData(listid)

    # If listing data exisits
    if listingData:
        # If the user is logged in, render listing page with user and listing data
        if session.get('user'):
            return render_template('listing.html', user=session['user'], listing=listingData)
        
        # If the user is not logged in, render listing page with listing data, but without user data
        else:
            return render_template('listing.html', listing=listingData)
   
    # If the listing does not exist, return error
    else:
        return "Listing not found", 404



## Functions ## 

def compareJobs(listids):
    '''
    Compares job listings based on the provided list of listids

    Args:
        listids (list): A list of job listids to compare

    Returns:
        list: A list of job listings including their attributes
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Base query for gathering listing attributes from the database
    query = """
        SELECT listid, title, company, position, salary, type, sourcelink, description
        FROM listing
        WHERE listid IN ({})
    """.format(','.join('?' for _ in listids))
    # Executing the query for the listings to be compared
    cursor.execute(query, tuple(listids))
    # Fetching attributes for each lisitng
    jobs = cursor.fetchall()

    # Close connection to the database and return jobs
    conn.close()
    return jobs



def allowedFile(filename):
    '''
    Checks if the provided file has an allowed extension, ensures that the file has a period (.) in
    its name and that the extension matches one of the defined allowed types

    Args:
        filename (str): The name of the file
    
    Returns:
        bool: True or False if the file is allowed or not
    '''

    # Return True or False depending on if the file has a period and is of an allowed type
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def getPassword(userid):
    '''
    Retrieves the password for a given user from the database for the given userid by querying
    the database for that users attributes

    Args:
        userid (int): The userid for the user
    
    Returns: 
        str: The stored password for the user
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Handling get password function
    try:
        # Querying the database for users password based on userid
        cursor.execute("SELECT password FROM user WHERE userid = ?", (userid,))
        # Fetching users information
        temp = cursor.fetchone()
        # Retrieve password from users attributes
        storedPassword = temp[0]
        # Return password
        return storedPassword

    # Exception handling
    except Exception as e:
        db.session.rollback()
        print(f"Error creating listings: {e}", "error")

    # Close connection to the database
    finally:
        conn.close()



def updatePassword(userid, newPassword):
    '''
    Updates the password for a user in the database with the provided new password and userid,
    executes a query to update the password attribute for a user based on their userid

    Args:
        userid (int): The userid of the user
        newPassword (str): The new password to be updated for the user
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Handling changing a users password
    try:
        # Querying the database to update a users password with the new password and user id
        conn.execute("UPDATE user SET password = ? WHERE userid = ?", (newPassword, userid,))
        conn.commit()

    # Exception handling
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)
    
    # Close connection to the database
    finally:
        conn.close()



def updatePersonalInfo(userid, username=None, profilePic=None):
    '''
    Updates the personal information, username and profile picture, for the user based on
    inputted username, profile picture, and userid. Updates the username and or profile picture
    by querying the database to update the attributes

    Args:
        userid (int): The userid of the user
        username (str, optional): The new username to be set for the user, default to None
        profilePic (str, optional): The new filepath for the profile picture to be set for the 
        user, defaults to None
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Handling updating personal info
    try:
        # If a new username is provided
        if username is not None:
            # Querying the database to update username with new username and userid
            cursor.execute("UPDATE user SET username = ? WHERE userid = ?", (username, userid))

        # If a new profile picture is provided
        if profilePic is not None:
            # Querying the database to update profile picture with new profile picture and userid
            cursor.execute("UPDATE user SET profilepic = ? WHERE userid = ?", (profilePic, userid))
        
        # Committing changes
        conn.commit()

    # Close connection to the database
    finally:
        conn.close()



def deleteUser(userid):
    '''
    Deletes a user from the database based on the given userid. Query the database to delete a user
    by passing a userid. Removes the user from the database

    Args:
        userid (int): The userid of the user
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Handling deleting a user
    try:
        # Querying the database to delete a user based on userid
        cursor.execute("DELETE FROM user WHERE userid = ?", (userid,))
        conn.commit()

    # Exception handling
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm)
    
    # Close connection to the database
    finally:
        conn.close()



def getSaved(userid, savedSearchQuery='', jobType=[], position=[]):
    '''
    Retrieves a list of saved job listings for a user based on optional filters

    Args:
        userid (int): The unique userid for a user
        savedSearchQuery (str, optional): A search term to filter job listings, defaults to an empty string
        jobType (list, optional): A list of job types to filter results by, defaults to an empty list
        position (list, optional): A list of positions to filter results by, defaults to an empty list

    Returns:
        jobs (list): A list of tuples representing a saved job listing(s), returns an empty list if no
        saved listings are found
    '''
    
    # Connecting to the database
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
    savedIds = [x[0] for x in savedIds]

    # Only proceed if there are saved listids
    if savedIds:
        # Base query for the database
        query = """
            SELECT listid, title, company, position, salary, type, sourcelink, description
            FROM listing
            WHERE listid IN ({})
        """.format(','.join('?' for _ in savedIds))
        
        # Parameters for the query, starting with savedIds and no filters
        params = savedIds

        # Adding the filter if a savedSearchQuery is provided
        if savedSearchQuery:
            searchPattern = f"%{savedSearchQuery}%"
            query += """
                AND (
                    title LIKE ? OR 
                    company LIKE ? OR 
                    position LIKE ? OR 
                    type LIKE ? OR 
                    description LIKE ?
                )
            """
            # Adding to the parameters with the search pattern
            params.extend([searchPattern] * 5)
        
        # Adding the filter if jobType is provided
        if jobType:
            like_clauses = [f"description LIKE ?" for _ in jobType]
            query += " AND (" + " OR ".join(like_clauses) + ")"
            # Adding to the parameters with the jobType
            params.extend([f"%{jt}%" for jt in jobType])

        # Adding the filter if position is provided
        if position:
            like_clauses = [f"salary LIKE ?" for _ in position]
            query += " AND (" + " OR ".join(like_clauses) + ")"
            # Adding to the parameters with the position
            params.extend([f"%{pos}%" for pos in position])
        
        # Execute the query with parameters
        cursor.execute(query, params)
        jobs = cursor.fetchall()

        # Close connection to database and return results
        conn.close()
        return jobs

    # If no savedIds are found
    else:
        # Close connection to database and return empty list
        conn.close()
        return []



def getData(listid):
    '''
    Retrieves attributes for a listing from the database

    Attributes:
        listid (int): The listid attribute for a specific listing entity

    Returns:
        listingData (tuple): A tuple containing attributes for a specific listing entity:
        listid, title, company, position, salary, type, sourcelink, description. Returns
        None if no listing with the given listid is found
    '''

    # Connecting to the database
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

    # Return listing data
    return listingData



def populateListings(searchTerm='', jobType=[], position=[]):
    '''
    Populates job listings for the home/index page based on search criteria

    Args:
        searchTerm (str, optional): A search term to filter job listings, defaults to an empty string
        jobType (list, optional): A list of job types to filter results by, defaults to an empty list
        position (list, optional): A list of positions to filter results by, defaults to an empty list

    Returns:
        list: A list of touples representing job listings, contains: listid, title, company, position
        salary, type, sourceLink, description
    '''

    # Connecting to the database
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    # Base query that retrieves all listings
    query = """
        SELECT listid, title, company, position, salary, type, sourcelink, description
        FROM listing
        WHERE 1=1
    """
    
    # List to store parameters for the query
    params = []

    # If a search term is provided, add to the query
    if searchTerm:
        like_pattern = f"%{searchTerm}%"
        query += " AND (title LIKE ? OR company LIKE ? OR position LIKE ? OR type LIKE ? OR description LIKE ?)"
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern, like_pattern])

    # If jobType is provided, add to the query
    if jobType:
        like_clauses = [f"description LIKE ?" for _ in jobType]
        query += " AND (" + " OR ".join(like_clauses) + ")"
        params.extend([f"%{jt}%" for jt in jobType])
    
    # If position is provided, add to the query
    if position:
        like_clauses = [f"salary LIKE ?" for _ in position]
        query += " AND (" + " OR ".join(like_clauses) + ")"
        params.extend([f"%{pos}%" for pos in position])
    
    # If no filters (searchTerm, jobType, position) are provided, we return all listings
    if searchTerm is None and jobType is None and position is None:
        query = """
            SELECT listid, title, company, position, salary, type, sourcelink, description
            FROM listing
        """
        params = []

    # Execute the query with parameters
    cursor.execute(query, params)
    
    # Fetching the results
    jobs = cursor.fetchall()

    # Closing the database connection
    conn.close()

    # Returning the retrieved jobs
    return jobs



def createListing():
    '''
    Creates listing entities in the database by reading from a CSV file

    This method reads from the CSV file 'listings.csv' generated by the web scraper 'jobScraper.py'
    then processes each row to retrieve listing attributes. These attributes are inserted into the 
    listings table in the database
    '''
    try:
        # Open the CSV file and read data
        with open('listings.csv', 'r') as csvFile:
            reader = csv.DictReader(csvFile)
            # Iterate through each row in the CSV file
            for row in reader:
                # Retreiving attributes for a listing from the CSV
                title = row["title"].strip()
                company = row["company"].strip()
                position = row["position"].strip()
                salary = row["salary"].strip()
                jobtype = row["type"].strip()
                sourcelink = row["sourceLink"].strip()
                description = row["description"].strip()

                # Reformatting descriptions due to commas causing collisions
                description = description.replace(';', ',')
                description = description.replace('~~', '\n')

                # Connecting to the database
                conn = sqlite3.connect('CareerSiftDB.db')
                cursor = conn.cursor()

                # Creating a new listing in the database
                cursor.execute("INSERT INTO listing (title, company, position, salary, type, sourcelink, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (title, company, position, salary, jobtype, sourcelink, description))
                
                # Commit the transaction
                conn.commit()
            # Closing connection
            conn.close()      

    # Error handling
    except FileNotFoundError:
        print("CSV file not found. Please ensure 'listings.csv' exists in the application directory.", "error")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating listings: {e}", "error")



# Function for removing listings (admin function) ## NEEDS WORK ##
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



## Main Method ##

if __name__ == '__main__':
    '''
    Checks if the script is being run as the main program, starts Flask application
    '''

    # Start the Flask application
    app.run(debug=True)