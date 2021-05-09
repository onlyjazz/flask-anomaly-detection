# flask-anomaly-detection
Implement a stateless micro-service that takes clinical JSON data structures
and  returns tagged anomalies.
The repo includes a Python Flask server for the micro-service as well as
Python model code that is executed on-demand.


NOTE: The flaskdata_api was developed in PyCharm development environment and tested on localhost

## HOW-TO setup
- git clone
- cd v1
- python -m venv flask_venv
- ./flask_venv/activate  # Activate the virtual environment
- python -m pip install --upgrade pip
- pip install -r requirements.txt

## HOW-TO run
- cd v1
- export FLASK_APP=server.py
- flask run

You should get this:
 * Serving Flask app "server.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

9/5/2021
Update requirements with missing module smclarify, move  flaskdata_superset.py to services, main Flask server to server.py in the same directory as settings.
