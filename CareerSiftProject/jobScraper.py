# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 20:00:26 2024

@author: yello
"""

# Importing requests, asyncio, csv, time, bs4, and selenium to allow for http requests, await, delays, and output using pip install 
import requests;
import asyncio;
import nest_asyncio;
import csv;
import time;

# God Itself, the scraper
from bs4 import BeautifulSoup;

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



# Link for indeed which is for Computer Science in only Charlotte
indeed = "https://www.indeed.com/jobs?q=Computer+Science&l=Charlotte%2C+NC&radius=0&start="
glassdoor = ""
snagajob = ""

allListingsUnfiltered = []

# Pretty much what the variable says
outputFileName = "indeedListings.csv"

"""
def getJobListings(link):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        price_element = soup.find()
        priceDec_element = soup.find()
        price = price_element.text.strip()
        priceDec = priceDec_element.text.strip()
        return (price+priceDec)
    else:
        print(link)
"""    
    
# Use beautiful soup to retrieve indeed job listings from link
def getIndeedListings():
    allListingsLink = []
    for i in range(2):
        # Opens the ChromeDriver application within the project file
        driver = webdriver.Chrome()
        # Obtains and loads the link for indeed
        driver.get(indeed + str(i*10))
        # Sleep time to allow for loading
        time.sleep(5)
        # Searches for the body of the page and presses the END key to account for "lazy loading"
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        # Allows lazy loading to occur
        time.sleep(3)  
        # Prints which page it is working on
        print("Link #" + str(i))
        # Creates an array of all the elements with the class name for each card on the page
        jobListingClass = driver.find_elements(By.CSS_SELECTOR, 'li.css-5lfssm.eu4oa1w0')
        #For each loop
        for listing in jobListingClass:
            try:
                # Try to find the job title link
                jobLinkElement = listing.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0')
                # Afer finding link, obtain the hred
                jobLink = jobLinkElement.get_attribute('href')
                # Appends the href to an array for all links
                allListingsLink.append(jobLink)
                # print(f"Found job link: {jobLink}")
            except Exception:
                try:
                    # Handle listings that are not advertised listings
                    jobLinkElement = listing.find_element(By.CSS_SELECTOR, 'h2.jobTitle a')
                    jobLink = jobLinkElement.get_attribute('href')
                    allListingsLink.append(jobLink)
                except Exception as e:
                    #Exception handling for not finding a listing
                    print("No job link found in this listing.")
        # Tell the console that scraping the page is complete
        print(f"Page {i+1} complete")
            
    # Self explanitory
    print("Indeed complete")
    # print("ALL job links: ", allListingsLink)
    # Closes out the ChromeDriver to allow for more resources
    driver.quit()
    # Calls the getIndeedListingInfo with an array of all the links obtained from each page
    getIndeedListingInfo(allListingsLink)
         


#Retrieve the information from getIndeedListings should be every page retreived from the pages searched. This will get the information from each page
def getIndeedListingInfo(allListingsLinkIndeed):
    # For each loop for all listings
    for listing in allListingsLinkIndeed:
        # Initializing an array for each item
        indeedInformation = []
        # Each item to be found
        jobTitle = ""
        jobDesc = ""
        jobPay = ""
        jobSite = "Indeed"
        applyLink = ""
        jobType = ""
        jobCompany = ""
        #Opens the webdriver
        driver = webdriver.Chrome()
        # Opens the link for this iteration of the loop
        driver.get(listing)
        #Loads page
        time.sleep(2)
        
        try:
            # Locate the job title using the CSS selector
            jobTitleElement = driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title")
            jobTitle = jobTitleElement.text.strip()
        except Exception as e:
            print("Could not find job title:", e)
            jobTitle = "NO TITLE FOUND"

        try:
            # Locate the company name using the CSS selector
            companyNameElement = driver.find_element(By.CSS_SELECTOR, "div[data-company-name='true'] a")
            companyName = companyNameElement.text.strip()
        except Exception as e:
            print("Could not find company name:", e)
            companyName = "NO COMPANY FOUND"

        try:
            # Locate the pay range using the CSS selector
            payRangeElement = driver.find_element(By.CSS_SELECTOR, "div#salaryInfoAndJobType span:nth-of-type(1)")
            payRange = payRangeElement.text.strip()
        except Exception as e:
            print("Could not find pay range:", e)
            payRange = "NO PAY RANGE FOUND"

        try:
            # Locate the job type using the CSS selector
            jobTypeElement = driver.find_element(By.CSS_SELECTOR, "div#salaryInfoAndJobType span:nth-of-type(2)")
            jobType = jobTypeElement.text.strip()
        except Exception as e:
            print("Could not find job type:", e)
            jobType = "NO JOB TYPE FOUND"
            
        try:
            # Locate the application link using the CSS selector
            applyButtonElement = driver.find_element(By.CSS_SELECTOR, "button[buttontype='primary']")
            applyLink = applyButtonElement.get_attribute('href')
        except Exception as e:
            print("Could not find application link:", e)
            applyLink = "NO APPLY LINK FOUND"

        

        #Adds the information to the array
        indeedInformation.append(listing)
        indeedInformation.append(jobTitle)
        indeedInformation.append(jobCompany)
        indeedInformation.append(jobPay)
        indeedInformation.append(jobDesc)
        indeedInformation.append(jobSite)
        indeedInformation.append(applyLink)
        indeedInformation.append(jobType)
        # Output the information to a file
        writeToIndeedFile(indeedInformation)
        driver.quit()
        


        # Use beautiful soup to retrieve glassdoor job listings from link
def getGlassDoorListings():
    return 1

# Use beautiful soup to retrieve snagajob job listings from link
def getSnagajobListings():
    return 1

# Find duplicates within all job listings scraped
def findDuplicates():
    for listing in allListingsUnfiltered:
        # TODO: SEARCH BY JOB TITLE, IF JOB TITLE IS SAME, CHECK IF DESC IS SAME
        print("")
        

# Outputs all information to a csv file after being filtered
def writeToIndeedFile(indeedListingInfo):
    # Opening a file and appends to it, hence the a.
    with open(outputFileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(indeedListingInfo)


    
         
while True:
    print("Opening Indeed")
    getIndeedListings()

    time.sleep(300) # Let the user actually see something!

