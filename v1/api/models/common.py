# Import libraries
import json
import pandas as pd
import category_encoders as ce
import pickle
from api.services import flaskdata_superset


def format_results(results):
    """
        Format pandas dataframe results as viewable json
        :param results:
    """
    parsed = json.loads(results.to_json())
    json_result = json.dumps(parsed, indent=4)
    return json_result


def format_parsed_json(results):
    """
        Format pandas dataframe results as viewable json
        :param results:
    """
    json_result = json.dumps(results, indent=4)
    return json_result


def format_json_to_rows(results):
    json_result = json.dumps(json.loads(results.reset_index().to_json(orient='records')), indent=2)
    return json_result


def final_response(results):
    json_result = json.dumps(json.loads(results), indent=2)
    return json_result


def get_key_and_values(input_data):
    data_dump = json.dumps(input_data)
    json_object = json.loads(data_dump)
    key_value_pairs = json_object.items()
    keys = json_object.keys()
    values = json_object.values()
    return list(keys), list(values), key_value_pairs


def get_data_for_cols(col_pair, ds_name):
    df_dataset = flaskdata_superset.get_data(ds_name)
    df_pairs_dataset = df_dataset[col_pair]
    return df_pairs_dataset


# ********************************************************************************************
# Start: Common functions for isotree and sklearn isolation forest methods
# ********************************************************************************************

# get data for column pairs
def get_pair_dataset_and_pair_full_dataset(col_pair, ds_name, use_full_data):
    df_dataset = flaskdata_superset.get_data(ds_name)
    if use_full_data == "Y":
        df_pairs_dataset = df_dataset[col_pair]
        cols = col_pair
    else:
        df_pairs_dataset = pd.DataFrame(col_pair)
        cols = list(df_pairs_dataset.columns.values)

    return df_pairs_dataset, cols


# hashing encoder method
def hashing_encoder(col_pair, num_components, df_pair_dataset):
    hashed_data = ce.HashingEncoder(cols=col_pair, n_components=num_components).fit_transform(df_pair_dataset)
    return hashed_data


# save pickle model
def save_model(clf, path_filename):
    with open(path_filename, 'wb') as f:
        pickle.dump(clf, f)


# load saved pickle model
def load_model(path_filename):
    with open(path_filename, 'rb') as f:
        clf = pickle.load(f)
    return clf

# ********************************************************************************************
# End: Common functions for isotree and sklearn isolation forest methods
# ********************************************************************************************
