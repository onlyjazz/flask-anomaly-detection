# flask-anomaly-detection
Implement a stateless micro-service that takes clinical JSON data structures and return tagged anomalies.
The repo includes a Python Flask server for the micro-service as well as
Python model code that is executed on-demand.


NOTE: The flaskdata_api was developed in PyCharm development environment and tested on localhost

## HOW-TO setup
- git clone
- cd v1
- python -m venv flask_venv
- ./flask_venv/bin/activate  # Activate the virtual environment
- python -m pip install --upgrade pip
- pip install -r requirements.txt

## Sample input payload for running the endpoints
Sample input payload can be found in the **sample_payload** folder

   Sample payload for e.g.
   Case 1: With a subset of datapoints for the column pair say aevent, age_group
    {
    "dataset_name": "adverse_events_subset",
    "pair_data": [
        {"aevent": "SINUS BRADYCARDIA", "age_group": " < 65"},
        {"aevent": "CONSTIPATION", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "DIARRHEA", "age_group": "< 65"},
        {"aevent": "NAUSEA", "age_group": "< 65"},
        {"aevent": "NAUSEA", "age_group": "< 65"},
        {"aevent": "ASTHENIA", "age_group": "< 65"},
        {"aevent": "NAUSEA", "age_group": "< 65"},
        {"aevent": "NAUSEA", "age_group": "< 65"},
        {"aevent": "VOMITING", "age_group": "< 65"},
        {"aevent": "FATIGUE", "age_group": "< 65"},
        {"aevent": "FATIGUE", "age_group": "< 65"},
        {"aevent": "FLU LIKE SYMPTOMS", "age_group": "< 65"},
        {"aevent": "FLU LIKE SYMPTOMS", "age_group": "< 65"},
        {"aevent": "FLU LIKE SYMPTOMS", "age_group": "< 65"}
    ],
    "threshold": 0.4,
    "use_existing_model": "N",
    "use_full_data": "N",
    "model_name": "AE"
}

Case 2: With all the data in the column pair say investigator, aevent
     {
    "dataset_name": "adverse_events_subset",
    "pair_data": ['investigator', 'aevent'],
    "threshold": 0.4,
    "use_existing_model": "N",
    "use_full_data": "N",
    "model_name": "AE"
	}

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


11/5/2021
Created assets and models folders.
v1/api/models contains python service code to run models

TODO - rename v1/api/models to v1/api/code and retest

20/5/2021
Fix RequestsDependencyWarning: urllib3 (1.25.2) or chardet (3.0.4) doesn't match a supported version warning
 pip install --upgrade requests
 Successfully installed requests-2.25.1
