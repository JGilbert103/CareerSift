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

# Link for indeed which is for Computer Science in only Charlotte
indeed = "https://www.indeed.com/jobs?q=Computer+Science&l=Charlotte%2C+NC&radius="
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
    for i in range(20):
        response = requests.get(indeed + str((i*10)))
        if response.status_code == 200:
         soup = BeautifulSoup(response.content, 'html.parser')
         
        else:
            print("Something went wrong in the indeed function")
         
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
def writeToFile(allJobListings):
    with open(outputFileName, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)


    
         
while True:
    for i in range (3):
        response = requests.get(indeed + str((i*10)))
        print(indeed + str((i*10)))
        print(response)
    time.sleep(5)