'''
ABOUT
Author: Owen Hartzell 801188721 ohartzel@charlotte.edu
For: ITSC 3155, Software Engineering, Fall 2024
Project: Final Project - Group 9, "CareerSift"
'''

## Imports ##
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import db

## Models ##

# Model for user
class user(db.Model):
    '''
    Represents a user in the system

    Attributes:
        userid (int): Unique identifier for the user, autoincremented
        username (str): Username for the user
        password (str): Password for the user
        email (str): Email address for the user
        isadmin (bool): Indicates if the user is an admin or not
    '''

    userid = db.Column('userid', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column('username', db.String(25))
    password = db.Column('password', db.String(25))
    email = db.Column('email', db.Text)
    isadmin = db.Column('isadmin', db.Boolean, default=False)

    def __init__(self, username, password, email, isadmin):
        '''
        Initializes a new user.

        Args:
            username (str): Username for the user
            password (str): Password for the user
            email (str): Email address for the user
            isadmin (bool): Indicates if the user is an admin or not
        '''

        self.username = username
        self.password = password
        self.email = email
        self.isadmin = isadmin



# Model for listing
class listing(db.Model):
    '''
    Represents a listing in the system

    Attributes: 
        listid (int): Unique identifier for listing, autoincremented
        title (str): Title for the listing
        company (str): Company of the listing
        position (str): Position of the listing
        salary (str): Salary of the listing
        type (str): Type of the listing
        sourceLink (str): Source link of the listing
        description (str): Description of the listing
    '''

    listid = db.Column('listid', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column('title', db.String(50))
    company = db.Column('company', db.String(50))
    position = db.Column('position', db.String(50))
    salary = db.Column('salary', db.String(25))
    type = db.Column('type', db.String(25))
    sourceLink = db.Column('sourceLink', db.Text)
    description = db.Column('description', db.Text)

    def __init__(self, title, company, position, salary, type, sourceLink, description):
        '''
        Initializes a new job listing.

        Args:
            title (str): Title for the listing
            company (str): Company of the listing
            position (str): Position of the listing
            salary (str): Salary of the listing
            type (str): Type of the listing
            sourceLink (str): Source link of the listing
            description (str): Description of the listing
        '''

        self.title = title
        self.company = company
        self.position = position
        self.salary = salary
        self.type = type
        self.sourceLink = sourceLink
        self.description = description



# Model for saved listing
class savedListing(db.Model):
    '''
    Represents the relationship between users and saved job listings

    Attributes:
        userid (int): Foreign key for the user
        listid (int): Foreign key for the listing
    '''

    __tablename__ = 'savedListing'

    userid = Column(Integer, ForeignKey('user.userid'), primary_key=True)
    listid = Column(Integer, ForeignKey('listing.listid'), primary_key=True)

    user = relationship('user', backref='savedListings')
    listing = relationship('listing', backref='savedbyusers')



# Model for messages
class messages(db.Model):
    '''
    Represents a message in the system
    
    Attributes:
        messageid (int): Unqique identifier for the message
        senderid (int): id of the sender, foreign key for user
        receiverid (int): id of the receiver, foreign key for user
        listid (int): id of the listing, foreign key for listing
        subject (str): Subject of the message
        messagebody (str): Content of the message
        timestamp (datetime): Time the message was sent
        isread (bool): Indicates if the message was read or not
    '''

    messageid = db.Column('messageid', db.Integer, primary_key=True)
    senderid = db.Column('senderid', db.Integer)
    receiverid = db.Column('receiverid', db.Integer)
    listid = db.Column('listid', db.Integer)
    subject = db.Column('subject', db.Text)
    messagebody = db.Column('messagebody', db.Text)
    #timestamp = db.Column('timestamp', db.) ## Add correct variable ##
    isread = db.Column('isread', db.Boolean, default=False)

    def __init__(self, messageid, senderid, receiverid, listid, subject, messagebody, timestamp, isread):
        '''
        Initializes a new message.

        Args:
            messageid (int): The message id
            senderid (int): The id of the sender
            receiverid (int): The id of the receiver
            listid (int): The id of the job listing associated with the message
            subject (str): The subject of the message
            messagebody (str): The body of the message
            timestamp (datetime): The time the message was sent
            isread (bool): If the message has been read
        '''

        self.messageid = messageid
        self.senderid = senderid
        self.receiverid = receiverid
        self.listid = listid
        self.subject = subject
        self.messagebody = messagebody
        self.timestamp = timestamp
        self.isread = isread



# Model for contact message
class contactMessage(db.Model):
    '''
    Represents a contact message in the system

    Attributes: 
        contactMessageId (int): Unique identifier for contact message
        email (str): The email of the sender
        issue (str): The contents of the message
    '''

    contactMessageId = db.Column('contactMessageId', db.Integer, primary_key=True, autoincrement=True)
    email = db.Column('email', db.String(75))
    issue = db.Column('issue', db.Text)

    def __init__(self, email, issue):
        '''
        Initializes a new contact message.

        Args:
            email (str): The email of the sender
            issue (str): The contents of the message sent by the sender
        '''

        self.email = email
        self.issue = issue