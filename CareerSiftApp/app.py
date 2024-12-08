import os 

import sqlite3
import csv
import bcrypt
from flask import Flask, redirect, url_for, render_template, request, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from database import db
from models import user, listing, savedListing, messages, contactMessage
from forms import RegisterForm, LoginForm, ContactForm, PersonalInfoForm, ChangePasswordForm, DeleteAccountForm
from werkzeug.utils import secure_filename

#import jobScraper

UPLOAD_FOLDER = 'static/profilepics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CareerSiftDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
                company = row["company"].strip()

                position = row["position"].strip()

                salary = row["salary"].strip()

                jobtype = row["type"].strip()

                sourcelink = row["sourceLink"].strip()

                description = row["description"].strip()

                description = description.replace(';', ',')
                description = description.replace('~~', '\n')

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
def populateListings(searchTerm='', jobType=[], position=[]):
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
        like_clauses = [f"description LIKE ?" for _ in jobType]  # Create LIKE clause for each jobType
        query += " AND (" + " OR ".join(like_clauses) + ")"  # Combine with OR
        params.extend([f"%{jt}%" for jt in jobType])
    
    # If position is provided, add to the query
    if position:
        like_clauses = [f"salary LIKE ?" for _ in position]  # Create LIKE clause for each position
        query += " AND (" + " OR ".join(like_clauses) + ")"  # Combine with OR
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



# Method to handle populating listings saved by a user
def getSaved(userid, savedSearchQuery='', jobType=[], position=[]):
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
        query = """
            SELECT listid, title, company, position, salary, type, sourcelink, description
            FROM listing
            WHERE listid IN ({})
        """.format(','.join('?' for _ in savedIds))
        
        params = savedIds

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
            params.extend([searchPattern] * 5)
            
        if jobType:
            like_clauses = [f"description LIKE ?" for _ in jobType]  # Create LIKE clause for each jobType
            query += " AND (" + " OR ".join(like_clauses) + ")"  # Combine with OR
            params.extend([f"%{jt}%" for jt in jobType])

        if position:
            like_clauses = [f"salary LIKE ?" for _ in position]  # Create LIKE clause for each position
            query += " AND (" + " OR ".join(like_clauses) + ")"  # Combine with OR
            params.extend([f"%{pos}%" for pos in position])

        '''else:
            # Query without a search term
            query = """
                SELECT listid, title, company, position, salary, type, sourcelink, description
                FROM listing
                WHERE listid IN ({})
            """.format(','.join('?' for _ in savedIds))
            params = savedIds'''
        
        # Execute the query with parameters
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        conn.close()
        return jobs
    else:
        conn.close()
        return []


###   Methods to handle register, login, and logout   ###

## Method for registering a user
@app.route('/register.html', methods=['POST', 'GET'])
def register():

    if session.get('user'):
        return redirect(url_for('index'))

    else:

        form = RegisterForm()

        if request.method == 'POST' and form.validate_on_submit():

            # Gathering user data entered to the application
            username = form.username.data
            email = form.email.data.strip() if form.email.data else None
            password = form.password.data

            # Create a new user object
            conn = sqlite3.connect('CareerSiftDB.db')
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
            existingUsername = cursor.fetchone()

            if existingUsername is not None:
                flash('Account already exisits with given username', 'error')
                conn.close()
                return redirect(url_for('register'))
            
            if email is not None:
                cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
                existingEmail = cursor.fetchone()

                if existingEmail is not None:
                    flash('Account already exisits with given email', 'error')
                    conn.close()
                    return redirect(url_for('register'))

            cursor.execute("INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                        (username, password, email,))
            conn.commit()

            cursor.execute("SELECT userid, username, password, email, profilepic FROM user WHERE username = ?", (username,))
            user = cursor.fetchone()

            conn.close()
            
            session['user'] = username
            session['userid'] = user[0]
            session['profilepic'] = user[4]

            # Redirect user to home/index page
            return redirect(url_for('index'))
    
    # If there was an error with registering, redirect to register form
    #flash('All fields must be full to register', 'error')
    return render_template('register.html', form=form)



## Method for logging in a user
@app.route('/login.html', methods=['POST', 'GET'])
def login():

    if session.get('user'):
        return redirect(url_for('index'))

    else:
        form = LoginForm()
        # Validating login form on submission
        if form.validate_on_submit():
            # If form is valid, searching the databse for the matching user
            conn = sqlite3.connect('CareerSiftDB.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT userid, username, password, email, profilepic FROM user WHERE username = ?", (form.username.data,))
            user = cursor.fetchone()

            # Checking user password
            if user and form.password.data == user[2]:
                # If the password is correct, adding the user to the session
                userid, username, password, email, profilepic = user

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
    searchTerm = request.args.get('search', '').strip()
    jobType = request.args.getlist('jobType')
    position = request.args.getlist('position')
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
    jobListings = populateListings(searchTerm, jobType, position)

    # Session verification and populating listings
    if session.get('user'):
        con = sqlite3.connect('CareerSiftDB.db')
        cursor = con.cursor()
        userid = session['userid']
        cursor.execute("SELECT listid FROM savedListing WHERE userid = ?", (userid,))

        userSavedListings = cursor.fetchall()
        userSavedListings = [x[0] for x in userSavedListings]

        con.close()

        return render_template("index.html", user=session['user'], jobs=jobListings, saved=userSavedListings)

    else:
        return render_template("index.html", jobs=jobListings)



# Method for save listings page
@app.route('/saveListing', methods=['POST'])
def saveListing():
    # Recieve the incoming json data from front end
    data = request.json
    temp = data.get('listid')
    listid = int(temp)

    try:
        userid = session['userid']
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        alreadySaved = cursor.fetchone()

        if alreadySaved is not None:
            return jsonify({'error': 'This listing is already saved by the user'}), 407

        cursor.execute("INSERT INTO savedListing (userid, listid) VALUES (?, ?)", (userid, listid))

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
    listid = int(temp)

    try:
        userid = session['userid']
        conn = sqlite3.connect('CareerSiftDB.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM savedListing WHERE userid = ? AND listid = ?", (userid, listid))
        deleteListing = cursor.fetchone()

        if deleteListing is None:
            return jsonify({'error': 'This listing is not saved by the user'}), 407

        cursor.execute("DELETE FROM savedListing where userid = ? AND listid = ?", (userid, listid))

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
@app.route('/compare', methods=['POST','GET'])
def compare():
    listids = request.args.getlist('compare')

    if session.get('user'):
        userid = session['userid']

        comparedJobs = compareJobs(listids)

        return render_template("compare.html", user=session['user'], jobs=comparedJobs)

    else:
        return render_template("compare.html")



def compareJobs(listids):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    query = """
        SELECT listid, title, company, position, salary, type, sourcelink, description
        FROM listing
        WHERE listid IN ({})
    """.format(','.join('?' for _ in listids))

    cursor.execute(query, tuple(listids))

    jobs = cursor.fetchall()
    
    conn.close()
    return jobs


## ADD SAVED FUNCTIONALITY
@app.route('/saved.html', methods=['GET'])
def saved():
    # Checking which users saved listings to access
    if session.get('user'):
        userid = session['userid']

        savedSearchQuery = request.args.get('search', '').strip()
        jobType = request.args.getlist('jobType')
        position = request.args.getlist('position')

        savedJobs = getSaved(userid, savedSearchQuery, jobType, position)

        return render_template("saved.html", user=session['user'], jobs=savedJobs)

    return redirect(url_for('login'))



@app.route('/savedlisting/<int:listid>')
def savedlisting(listid):

    listingData = getData(listid)

    if listingData:
        if session.get('user'):
            return render_template('savedlisting.html', user=session['user'], listing=listingData)
        else:
            return render_template('savedlisting.html', listing=listingData)
    else:
        return "Listing not found", 404



# Method for settings page
@app.route('/settings.html', methods=['POST','GET'])
def settings():
    # Checking which users settings to access
    if session.get('user'):

        personalInfoForm = PersonalInfoForm()
        changePasswordForm = ChangePasswordForm()
        deleteAccountForm = DeleteAccountForm()

        if request.method == 'POST':
            userid = session['userid']
            formType = request.form.get('form')

            if formType == 'PersonalInfoForm' and personalInfoForm.validate_on_submit():
                username = personalInfoForm.username.data
                profilePic = personalInfoForm.profilePic.data

                if username is None and profilePic is None:
                    #flash("Please provide a new username or upload a profile picture.", "personal-info-error")
                    return redirect(url_for('settings'))

                try:
                    if username:
                        updatePersonalInfo(userid, username=username)
                        #flash("Personal Information updated successfully!", "personal-info-success")

                except Exception as e:
                    flash(f"An error occurred: {e}", "danger")

                try:
                    if profilePic and allowedFile(profilePic.filename):
                        filename = secure_filename(profilePic.filename)

                        newFilename = f"user_{userid}_{filename}"

                        profilePath = os.path.join(app.config['UPLOAD_FOLDER'], newFilename)

                        profilePic.save(profilePath)

                        profilePicUrl = f"/static/profilepics/{newFilename}"

                        updatePersonalInfo(userid, profilePic=profilePicUrl)

                except Exception as e:
                    flash(f"An error occurred: {e}", "danger")
                
                #flash("Please provide a new username or upload a profile picture.", "personal-info-error")
                return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm) 

            #if notificationsForm.validate_on_submit():

            elif formType == 'ChangePasswordForm' and changePasswordForm.validate_on_submit():
                currentPassword = changePasswordForm.currentPassword.data
                newPassword = changePasswordForm.newPassword.data

                try:
                    storedPassword = getPassword(userid)

                    if storedPassword != currentPassword:
                        flash('Invalid current password', 'error')
                        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm) 

                    updatePassword(userid, newPassword)

                except Exception as e:
                    #flash(f"An error occurred: {e}", "danger")
                    return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)

            elif formType == 'DeleteAccountForm' and deleteAccountForm.validate_on_submit():
                try:
                    deleteUser(userid)
                    return redirect(url_for('logout'))
                except Exception as e:
                    #flash(f"An error occurred: {e}", "danger")
                    return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)


        # Redirect user to their settings page
        #flash('Invalid current password', 'error')
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)    
    else:
        # Redirect user to settings page
        return redirect(url_for('login'))   



def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def getPassword(userid):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password FROM user WHERE userid = ?", (userid,))
        temp = cursor.fetchone()
        storedPassword = temp[0]
        return storedPassword

    except Exception as e:
        db.session.rollback()
        print(f"Error creating listings: {e}", "error")
    finally:
        conn.close()



def updatePassword(userid, newPassword):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    try:
        conn.execute("UPDATE user SET password = ? WHERE userid = ?", (newPassword, userid,))
        conn.commit()

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm, deleteAccountForm=deleteAccountForm)
    
    finally:
        conn.close()



def updatePersonalInfo(userid, username=None, profilePic=None):

    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()
    try:
        if username is not None:
            cursor.execute("UPDATE user SET username = ? WHERE userid = ?", (username, userid))

        if profilePic is not None:
            cursor.execute("UPDATE user SET profilepic = ? WHERE userid = ?", (profilePic, userid))
        
        conn.commit()

    
    finally:
        conn.close()



def deleteUser(userid):
    conn = sqlite3.connect('CareerSiftDB.db')
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM user WHERE userid = ?", (userid,))
        conn.commit()

    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return render_template("settings.html", user=session['user'], personalInfoForm=personalInfoForm, changePasswordForm=changePasswordForm)
    
    finally:
        conn.close()



# Method for listing page
@app.route('/listings/<int:listid>', methods=['GET'])
def listings(listid):
    listingData = getData(listid)

    if listingData:
        if session.get('user'):
            return render_template('listing.html', user=session['user'], listing=listingData)
        else:
            return render_template('listing.html', listing=listingData)
    else:
        return "Listing not found", 404




## Main Method
if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=True)

    
