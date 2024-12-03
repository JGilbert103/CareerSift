import sqlite3
import csv

def createListing(dbPath, csvPath):
    # Connect to the SQLite database using the passed dbPath
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()
    
    try:
        # Open the CSV file and read data
        with open(csvPath, 'r') as file:  # Use csvPath here
            reader = csv.DictReader(file)
            
            # Iterate through each row in the CSV file
            for row in reader:
                # Insert listing data into the listing table
                cursor.execute('''
                    INSERT INTO listing (listid, position, company, salary, type, source, sourceLink, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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


# Main section to execute the function
if __name__ == "__main__":
    dbPath = 'CareerSiftApp/database.db'
    csvPath = 'CareerSiftApp/listings.csv'

    createListing(dbPath, csvPath)