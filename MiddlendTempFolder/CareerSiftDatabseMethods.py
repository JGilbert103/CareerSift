import sqlite3
import csv

#Function to add a user to the database
def add_user(dbPath, username, password, email, isadmin): #ADD PATH TO DATABASE
    # Connect to the SQLite database
    conn = sqlite3.connect() #ADD PATH TO DATABASE
    cursor = conn.cursor()
    
    try:
        # Insert a new user into the user table
        cursor.execute('''
            INSERT INTO user (username, password, email)
            VALUES (?, ?, ?, ?)
        ''', (username, password, email))
        
        # Commit the transaction
        conn.commit()
        print("User added successfully.")
    
    except sqlite3.Error as e:
        # Handle any database errors
        print("Error adding user:", e)
    
    finally:
        # Close the connection
        conn.close()

#Function to add a listing to the database
def createListing(dbPath, csvPath): #ADD PATH TO DATABSE AND CSV
    # Connect to the SQLite database
    conn = sqlite3.connect() #ADD PATH TO DATABASE
    cursor = conn.cursor()
    
    try:
        # Open the CSV file and read data
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            
            # Iterate through each row in the CSV file
            for row in reader:
                # Insert listing data into the listing table
                cursor.execute('''
                    INSERT INTO listing (listid, position, company, salary, type, source, sourceLink, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['position'],
                    row['company'],
                    row['salary'],
                    row['description'],
                    row['source'],
                    row['sourceLink'],
                    row['type']
                ))
        
        # Commit the transaction
        conn.commit()
        print("Listings created successfully from CSV.")
    
    except sqlite3.Error as e:
        # Handle any database errors
        print("Error creating listings from CSV:", e)
    
    finally:
        # Close the connection
        conn.close()

#Function for users to save a listing 
def saveListing(dbPath, userid, listid): #ADD PATH TO DATABASE
    # Connect to the SQLite database
    conn = sqlite3.connect() #ADD PATH TO DATABASE
    cursor = conn.cursor()
    
    try:
        # Insert into the savedListing table
        cursor.execute('''
            INSERT INTO savedListing (userid, listid)
            VALUES (?, ?)
        ''', (userid, listid))
        
        # Commit the transaction
        conn.commit()
        print("Listing saved successfully.")
    
    except sqlite3.IntegrityError:
        # Handle case where the listing is already saved
        print("This listing is already saved by the user.")
    
    except sqlite3.Error as e:
        # Handle any other database errors
        print("Error saving listing:", e)
    
    finally:
        # Close the connection
        conn.close()

#Function for admins to be able to delete listings
def remove_listing(dbPath, listid):
    # Connect to the SQLite database
    conn = sqlite3.connect() #ADD PATH TO DATABASE
    cursor = conn.cursor()
    
    try:
        # Delete the listing with the specified listid
        cursor.execute("DELETE FROM listing WHERE listid = ?", (listid,))
        
        # Check if any row was deleted
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Listing with ID {listid} removed successfully.")
        else:
            print(f"No listing found with ID {listid}.")
    
    except sqlite3.Error as e:
        # Handle database errors
        print("Error removing listing:", e)
    
    finally:
        # Close the connection
        conn.close()

