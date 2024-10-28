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

# NVM this is God. Beautiful soup is good and all, but Indeed does NOT like it
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



# Link for indeed which is for Computer Science in only Charlotte
indeed = "https://www.indeed.com/jobs?q=Computer+Science&l=Charlotte%2C+NC&radius=0&start="
glassdoor = ""
snagajob = "https://www.snagajob.com/search?q=computer+science&w=charlotte&radius=5&page="

allListingsUnfiltered = []

# Pretty much what the variable says
IndeedOutputFileName = "indeedListings.csv"
GlassdoorOutputFileName = "glassdoorListings.csv"
 
    
# Use beautiful soup to retrieve indeed job listings from link
def getIndeedListings():
    allListingsLink = []
    for i in range(2):
        # Opens the ChromeDriver application within the project file
        driver = webdriver.Chrome()
        # Obtains and loads the link for indeed
        driver.get(indeed + str(i*10))
        # Sleep time to allow for loading
        time.sleep(3)
        # Searches for the body of the page and presses the END key to account for "lazy loading"
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        # Allows lazy loading to occur
        time.sleep(2)  
        # Prints which page it is working on
        # print("Link #" + str(i))
        # Creates an array of all the elements with the class name for each card on the page
        jobListingClass = driver.find_elements(By.CSS_SELECTOR, 'li.css-1ac2h1w.eu4oa1w0')
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
    print("Running getIndeedListingInfo")
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
        driver.maximize_window()
        # Opens the link for this iteration of the loop
        driver.get(listing)
        #Loads page
        time.sleep(3)
        
        try:
            # Locate the job title using the CSS selector
            jobTitleElement = driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title")
            jobTitle = jobTitleElement.text.strip()
        except Exception as e:
            print("Could not find job title:", e)
            jobTitle = "NO TITLE FOUND"
            brokenLinks(listing)

        try:
            # Locate the company name using the CSS selector
            companyNameElement = driver.find_element(By.CSS_SELECTOR, "div[data-company-name='true'] a")
            jobCompany = companyNameElement.text.strip()
        except Exception as e:
            print("Could not find company name:", e)
            jobCompany = "NO COMPANY FOUND"
            brokenLinks(listing)

        try:
            # Locate the job description using the CSS selector
            jobDescElement = driver.find_element(By.CSS_SELECTOR, "div.jobsearch-JobComponent-description")
            jobDesc = jobDescElement.text.strip()
            
            # Check if "Full job description" is present and slice the text from that point onward
            keyword = "Full job description"
            if keyword in jobDesc:
                jobDesc = jobDesc.split(keyword, 1)[-1].strip()  # Keep everything after "Full job description"
            
            # Remove all commas and replace them with semi colons (fix after display on website due to csv issues)
            jobDesc = jobDesc.replace(',', ';')
            # Remove any newlines and replace them with spaces
            jobDesc = jobDesc.replace('\n', ' ')
        except Exception as e:
            print("Could not find job description:", e)
            jobDesc = "NO JOB DESCRIPTION FOUND"
            brokenLinks(listing)

        try:
            # Locate the salary or job type section
            salaryInfoDiv = driver.find_element(By.CSS_SELECTOR, "div#salaryInfoAndJobType")
            
            # Find all spans inside salaryInfoDiv
            spans = salaryInfoDiv.find_elements(By.CSS_SELECTOR, "span")
            
            # Initialize empty variables
            jobPay = "NO PAY RANGE FOUND"
            jobType = "NO JOB TYPE FOUND"
            
            if len(spans) > 0:
                # First span might contain pay, check for numbers or dollar sign
                if any(char.isdigit() for char in spans[0].text) or "$" in spans[0].text:
                    jobPay = spans[0].text.strip()
                
                # Check if second span exists for job type
                if len(spans) > 1:
                    jobType = spans[1].text.strip()
                    jobType = jobType.replace('-', ' ')
                    jobType = jobType.replace(',', '-')
                else:
                    # If there's only one span, it might be the job type, not salary
                    if "Full-time" in spans[0].text or "Part-time" in spans[0].text or "Contract" in spans[0].text:
                        jobType = spans[0].text.strip()
                        jobType = jobType.replace('-', ' ')
                        jobType = jobType.replace(',', '-')
        except Exception as e:
            print("Error finding pay and job type:", e)
            jobPay = "NO PAY RANGE FOUND"
            jobType = "NO JOB TYPE FOUND"
            brokenLinks(listing)


            
        try:
            # Try to find the external application button first
            applyButtonElement = driver.find_element(By.CSS_SELECTOR, "button[buttontype='primary'][href]")
            applyLink = applyButtonElement.get_attribute('href')
            print(f"External application link found: {applyLink}")
        except Exception:
            try:
                # If no external button, look for the internal Indeed apply form
                applyFormElement = driver.find_element(By.CSS_SELECTOR, "form[action]")
                applyLink = "Apply on Indeed- " + listing
            except Exception as e:
                print("Could not find application link:", e)
                applyLink = "NO APPLY LINK FOUND"
                brokenLinks(listing)

        

        #Adds the information to the array
        # LISTING LINK FOR DEBUGGING
        # indeedInformation.append(listing)
        # Information
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
    print("Ending ListingInfo")
        


        # Use beautiful soup to retrieve glassdoor job listings from link

def getGlassDoorListings():
    return 1

# Use beautiful soup to retrieve snagajob job listings from link
def getSnagajobListings():
    allListingsLink = []
    for i in range(2):
        driver = webdriver.Chrome()
        driver.get(snagajob + str(i+1))
        time.sleep(3)
        # Scroll down the page to load lazy images
        time.sleep(2)
        jobListingClass = driver.find_elements(By.CSS_SELECTOR, 'job-card')
        for listing in jobListingClass:
            try:
                jobLinkElement = listing.find_element(By.CSS_SELECTOR, 'meta[itemprop="url"]')
                jobLink = jobLinkElement.get_attribute('content')
                allListingsLink.append(jobLink)
            except:
                print("Could not find any job listing")
        driver.quit()
    getSnagajobListingInfo(allListingsLink)

def getSnagajobListingInfo(allListingsLinkGlassdoor):
    for listing in allListingsLinkGlassdoor:
        # Initializing an array for each item
        glassDoorInformation = []
        # Each item to be found
        jobTitle = ""
        jobDesc = ""
        jobPay = ""
        jobSite = "Snagajob"
        applyLink = ""
        jobType = ""
        jobCompany = ""
        #Opens the webdriver
        driver = webdriver.Chrome()
        driver.maximize_window()
        # Opens the link for this iteration of the loop
        driver.get(listing)
        #Loads page
        time.sleep(3)
        try:
            try:
                payElement = driver.find_element(By.CSS_SELECTOR, 'td[data-snagtag="job-est-wage"]')
                jobPay = payElement.text
                print(jobPay)
            except:
                try:
                    payElement = driver.find_element(By.CSS_SELECTOR, 'td[data-snagtag="job-wage"]')
                    jobPay = payElement.text
                    print(jobPay)
                except:
                    print("Something went wrong finding the pay")
        except:
            print("Could not find pay attribute")
            jobPay = "NO PAY RANGE FOUND"

        try:
            jobTypeElement = driver.find_element(By.CSS_SELECTOR, 'td[data-snagtag="job-categories"]')
            jobType = jobTypeElement.text
            jobType = jobType.replace('-', ' ')
            jobType = jobType.replace(',', '-')
        except:
            print("Could not find job type attribute")
            jobType = "NO JOB TYPE FOUND"



# Find duplicates within all job listings scraped
def findDuplicates():
    for listing in allListingsUnfiltered:
        # TODO: SEARCH BY JOB TITLE, IF JOB TITLE IS SAME, CHECK IF DESC IS SAME
        print("")
        

# Outputs all information to a csv file after being filtered
def writeToIndeedFile(indeedListingInfo):
    # Opening a file and appends to it, hence the a.
    with open(IndeedOutputFileName, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(indeedListingInfo)

def brokenLinks(link):
    with open("brokenIndeedLinks.csv", 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(link)
    
         
while True:
    print("Opening Indeed")
    getIndeedListings()
    # getSnagajobListings()

    time.sleep(300) # Let the user actually see something!

