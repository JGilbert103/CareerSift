-- Database tables for CareerSift website

--CREATE TABLE careersift (
--    webaddress INTEGER,
--    userList VARCHAR(25),
--    PRIMARY KEY(webaddress)
--);

-- Tables for user
CREATE TABLE IF NOT EXISTS user (
    userid INTEGER PRIMARY KEY,
    username VARCHAR(25),
    password VARCHAR(25),
    email VARCHAR(75),
    isadmin BOOLEAN DEFAULT FALSE
);

-- Adding a user for testing
INSERT INTO user (userid, username, password, email, isadmin)
VALUES(0, 'owen', 'P@ssw0rd!', 'ohartzel@charlotte.edu', TRUE);

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

-- Adding a saved listing for testing
INSERT INTO savedListing (userid, listid)
VALUES (0, 0);

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

CREATE TABLE contactMessage (
    contactMessageId INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(75),
    issue TEXT
);