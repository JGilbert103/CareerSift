# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 20:00:26 2024

@author: yello
"""

# Importing requests, asyncio, csv, and time to allow for http requests, await, delays, and output
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
outputFileName = "jobListings.csv"

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
        driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
        driver.get(indeed + str(i*10))
        time.sleep(5)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(3)  
        print("Link #" + str(i))
        jobListingClass = driver.find_elements(By.CSS_SELECTOR, 'li.css-5lfssm.eu4oa1w0')
        for listing in jobListingClass:
            try:
                # Try to find the job title link
                jobLinkElement = listing.find_element(By.CSS_SELECTOR, 'a.jcs-JobTitle.css-jspxzf.eu4oa1w0')
                jobLink = jobLinkElement.get_attribute('href')
                allListingsLink.append(jobLink)
                print(f"Found job link: {jobLink}")  # Print the link for debugging
            except Exception:
                try:
                    # Handle listings with a more complex structure
                    jobLinkElement = listing.find_element(By.CSS_SELECTOR, 'h2.jobTitle a')
                    jobLink = jobLinkElement.get_attribute('href')
                    allListingsLink.append(jobLink)
                    print(f"Found complex job link: {jobLink}")
                except Exception as e:
                    print(f"No job link found in this listing. Error: {e}")
        
        print(f"Page {i+1} complete")
            
    print("Indeed complete")
    # print("ALL job links: ", allListingsLink)
    driver.quit()
    getIndeedListingInfo(allListingsLink)
         


#Retrieve the information from getIndeedListings should be every page retreived from the pages searched. This will get the information from each page
def getIndeedListingInfo(allListingsLinkIndeed):
    for listing in allListingsLinkIndeed:
        indeedInformation = []
        jobTitle = ""
        jobDesc = ""
        jobPay = ""
        jobSite = "Indeed"
        applyLink = ""
        jobType = ""
        jobCompany = ""
        #Opens the webdriver
        driver = webdriver.Chrome()
        driver.get(listing)
        time.sleep(3)
        


        indeedInformation.append(jobTitle)
        indeedInformation.append(jobDesc)
        indeedInformation.append(jobPay)
        indeedInformation.append(jobSite)
        indeedInformation.append(applyLink)
        indeedInformation.append(jobType)
        indeedInformation.append(jobCompany)
        writeToIndeedFile(indeedInformation)
        


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
    with open(outputFileName, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)


    
         
while True:
    # for i in range (3):
    #     response = requests.get(indeed + str((i*10)))
    #     print(indeed + str((i*10)))
    #     print(response)
    # time.sleep(5)
    print("Opening Indeed")
    getIndeedListings()
    time.sleep(120) # Let the user actually see something!

