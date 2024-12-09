Hello and welcome to the CareerSift application!
Listed below are the steps and requirements to run our application

Requirements:
Python 3.7 or later
Download and install Python from https://www.python.org/downloads/

Pip (Python package installer)
Pip is included with puthon, to ensure it is active open a command line interface tool and enter the following
pip -- version

Virtual Environment (Optional, but recommended)
Creating a virtual environment helps avoid conflicts

Installation steps:
Clone the source code from our repository using a command line interface tool
git clone https://github.com/JGilbert103/CareerSift

Change directory to the repository folder
cd <repository folder>

Set up virtual environment using a command line interface tool, from the application directory
python 3 -m venv venv
source venv/bin/activate (FOR MACOS AND LINUX USERS)
venv\Scripts\activate (FOR WINDOWS USERS)

Install required packages
pip install -r requirements.text

Starting and running the application
flask run

Terminating the applicaiton
ctrl + c