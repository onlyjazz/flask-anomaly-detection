# flask-anomaly-detection
Implement a stateless micro-service that takes clinical JSON data structures
and  returns tagged anomalies.
The repo includes a Python Flask server for the micro-service as well as
Python model code that is executed on-demand.


NOTE: The flaskdata_api was developed in PyCharm development environment and tested on localhost

## HOW-TO
git clone
cd v1
python -m venv flask_venv
flask_venv\Scripts\activate.bat  # Activate the virtual environment
python -m pip install --upgrade pip
pip install -r requirements.txt
