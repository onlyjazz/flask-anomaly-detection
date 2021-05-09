import pandas as pd
import requests
import json


def authorize():
    """
        Get flaskdata rest-api authorization key
        :param
    """
    # set headers, url and payload
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    data = {"email": "omdenadata", "password": "12345678Od"}
    url = "https://dev-api.flaskdata.io/auth/authorize"

    # call flaskdata api to get the authorization key
    response = requests.post(url, headers=headers, json=data)
    auth_key = response.json()["token"]
    return auth_key


def get_data(table_name):
    """
        Fetch the data by table_name from calling flaskdata rest api with the
        the authorization key
        :param table_name:
    """
    # get the authorization key, which will be used to fetch the table data
    auth_key = authorize()

    # set headers, url and payload
    headers = {
        'Content-type': 'application/json',
        'Authorization': auth_key,
        'EDC': 'omdena'
    }
    url = 'https://dev-api.flaskdata.io/edc/study/extract-data'
    payload = {"tableName": table_name}  # e.g. "adae_adverse_events_reduced"

    # call the flaskdata api to fetch the superset data for the table (table_name)
    response = requests.post(url=url,
                             headers=headers,
                             data=json.dumps(payload))

    # get the response json
    data = response.json()
    # convert to pandas dataframe and return the dataframe
    df_data = pd.DataFrame.from_dict(data)

    return df_data