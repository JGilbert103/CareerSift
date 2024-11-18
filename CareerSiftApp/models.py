from database import db

## Create models

class User(db.Model):
    userid = db.Column('userid', db.Integer, primary_key=True)
    username = db.Column('username', db.String(25))
    password = db.Column('password', db.String(25))
    email = db.Column('email', db.string(75))
    isadmin = db.Column('isadmin', db.Boolean)

    def __init__(self, userid, username, password, email, isadmin)
        self.userid = userid
        self.username = username
        self.password = password
        self.email = email
        self.isadmin = isadmin

class Listing(db.model):
    listid = db.Column('listid', db.Integer, primary_key=True)
    position = db.Column('position', db.String(50))
    company = db.Column('company', db.String(50))
    salary = db.Column('salary', db.String(25))
    type = db.Column('type', db.String(25))
    sourceLink = db.Column('sourceLink', db.Text)
    description = db.Column('description', db.Text)

    def __init__(self, listid, position, company, salary, type, sourceLink, description)
        self.listid = listid
        self.position = position
        self.company = company
        self.salary = salary
        self.type = type
        self.sourceLink = sourceLink
        self.description = description

class SavedListing(db.model):

## Create model for saved listing ##

class Messages(db.model):
    messageid = db.Column('messageid', db.Integer, primary_key=True)
    senderid = db.Column('senderid', db.Integer)
    receiverid = db.Column('receiverid', db.Integer)
    listid = db.Column('listid', db.Integer)
    subject = db.Column('subject', db.Text)
    messagebody = db.Column('messagebody', db.Text)
    timestamp = db.Column('timestamp', db.) ## Add correct variable ##
    isread = db.Column('isread', db.Boolean, default=False)

    def __init__(self, messageid, senderid, receiverid, listid, subject, messagebody, timestamp, isread)
        self.messageid = messageid
        self.senderid = senderid
        self.receiverid = receiverid
        self.listid = listid
        self.subject = subject
        self.messagebody = messagebody
        self.timestamp = timestamp
        self.isread = isread