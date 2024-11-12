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
    isadmin BOOLEAN DEFAULT FALSE,
);

-- Adding a user for testing
INSERT INTO user (userid, username, password, email, isadmin)
VALUES(0, owen, P@ssw0rd!, ohartzel@charlotte.edu, true);

-- Tables for listings
CREATE TABLE listing (
    listid INTEGER PRIMARY KEY,
    position VARCHAR(50),
    company VARCHAR(50),
    salary VARCHAR(25),
    type VARCHAR(25),
    source VARCHAR(25),
    sourceLink TEXT,
    description TEXT,
);

-- Adding a listing for testing
INSERT INTO listing (listid, position, company, salary, type, source, sourceLink, description)
VALUES(0, fake position, fake company, $0 a year, remote, linkedout, https://www.google.com/search?q=google&oq=google&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIYCAEQLhhDGIMBGMcBGLEDGNEDGIAEGIoFMgYIAhBFGDwyBggDEEUYPDIGCAQQRRg8MgYIBRBFGDwyBggGEEUYPDIGCAcQRRhB0gEIMTI5M2owajeoAgCwAgA&sourceid=chrome&ie=UTF-8, this is a fake job listing for test purposes);

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

