# flask-anomaly-detection
Implement a stateless micro-service that takes clinical JSON data structures
and  returns tagged anomalies.
The repo includes a Python Flask server for the micro-service as well as
Python model code that is executed on-demand.

## *********************************************************************************************************

# NOTE: The flaskdata_api was developed in PyCharm development environment and tested on localhost

# Task: Steps to take to get the flaskdata_api_v1.0 up and running
The following steps need to be taken after doing a git clone

## Step 1: change directory
cd flaskdata_api_v1.0

## Step 2: create a virtual environment as flask_venv (or your name of choice)
python -m venv flask_venv

## Step 3: call the activate.bat to activate the virtual environment
flask_venv\Scripts\activate.bat

## Step 4: do a pip upgrade
python -m pip install --upgrade pip

## Step 5: pip install all the requirements
pip install -r requirements.txt

## *********************************************************************************************************