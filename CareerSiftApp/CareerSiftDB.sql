-- Tables for user
CREATE TABLE IF NOT EXISTS user (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(25),
    password TEXT,
    email VARCHAR(75),
    isadmin BOOLEAN DEFAULT FALSE,
    profilepic TEXT DEFAULT '/static/default.png'
);

-- Tables for listings
CREATE TABLE listing (
    listid INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(50),
    company VARCHAR(50),
    position VARCHAR(50),
    salary VARCHAR(25),
    type VARCHAR(25),
    sourceLink TEXT,
    description TEXT
);

-- Tables for saved listings
CREATE TABLE savedListing (
    userid INTEGER,
    listid INTEGER,
    
    PRIMARY KEY (userid, listid),
    FOREIGN KEY (userid) REFERENCES user(userid),
    FOREIGN KEY (listid) REFERENCES listing(listid)
);

-- Tables for messages
CREATE TABLE messages (
    messageid INTEGER PRIMARY KEY,
    senderid INTEGER,
    receiverid INTEGER,
    listid INTEGER,
    subject TEXT,
    messagebody TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    isread BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (senderid) REFERENCES user(userid),
    FOREIGN KEY (receiverid) REFERENCES user(userid),
    FOREIGN KEY (listid) REFERENCES listing(listid)
);

-- Tables for contact messages
CREATE TABLE contactMessage (
    contactMessageId INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(75),
    issue TEXT
);