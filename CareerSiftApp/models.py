from database import db
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class user(db.Model):
    userid = db.Column('userid', db.Integer, primary_key=True)
    username = db.Column('username', db.String(25))
    password = db.Column('password', db.String(25))
    email = db.Column('email', db.String(75))
    isadmin = db.Column('isadmin', db.Boolean)

    def __init__(self, userid, username, password, email, isadmin):
        self.userid = userid
        self.username = username
        self.password = password
        self.email = email
        self.isadmin = isadmin

class listing(db.Model):
    listid = db.Column('listid', db.Integer, primary_key=True)
    title = db.column('title', db.String(50))
    company = db.Column('company', db.String(50))
    position = db.Column('position', db.String(50))
    salary = db.Column('salary', db.String(25))
    type = db.Column('type', db.String(25))
    sourceLink = db.Column('sourceLink', db.Text)
    description = db.Column('description', db.Text)

    def __init__(self, listid, title, company, position, salary, type, sourceLink, description):
        self.listid = listid
        self.title = title
        self.company = company
        self.position = position
        self.salary = salary
        self.type = type
        self.sourceLink = sourceLink
        self.description = description

class savedListing(db.Model):
    __tablename__ = 'savedListing'

    userid = Column(Integer, ForeignKey('user.userid'), primary_key=True)
    listid = Column(Integer, ForeignKey('listing.listid'), primary_key=True)

    user = relationship('user', backref='savedListings')
    listing = relationship('listing', backref='savedbyusers')

class messages(db.Model):
    messageid = db.Column('messageid', db.Integer, primary_key=True)
    senderid = db.Column('senderid', db.Integer)
    receiverid = db.Column('receiverid', db.Integer)
    listid = db.Column('listid', db.Integer)
    subject = db.Column('subject', db.Text)
    messagebody = db.Column('messagebody', db.Text)
    #timestamp = db.Column('timestamp', db.) ## Add correct variable ##
    isread = db.Column('isread', db.Boolean, default=False)

    def __init__(self, messageid, senderid, receiverid, listid, subject, messagebody, timestamp, isread):
        self.messageid = messageid
        self.senderid = senderid
        self.receiverid = receiverid
        self.listid = listid
        self.subject = subject
        self.messagebody = messagebody
        self.timestamp = timestamp
        self.isread = isread