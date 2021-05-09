# Import libraries
import sys
import pandas as pd
import numpy as np
from api.models import common
from api.models import train_isotree_model

# add paths to sys
sys.path.insert(0, 'models')
sys.path.insert(1, 'assets/models')


def get_anomaly_isotree(col_pair, ds_name, use_full_data, use_existing_model,
                        model_for, model_path, threshold=0.5, n_components=32):
    """
        Method: Get anomaly detection
        :param col_pair:
        :param ds_name:
        :param model_for:
        :param model_path:
        :param use_full_data:
        :param use_existing_model:
        :param threshold:
        :param n_components:
        :return: a dataframe with 4 columns: pair of variables, isotree_score, is_anomaly

    """
    # ** STEP 1 **
    # get the data for the col_pairs - depending on the conditions
    df_pairs_dataset, cols = common.get_pair_dataset_and_pair_full_dataset(col_pair, ds_name,
                                                                           use_full_data)

    # ** STEP 2 **
    # Feature Engineering: transform the categorical values into numerical data
    is_imputer = False

    # apply the hashing encoder hashing_encoder
    # n_components = 32
    df_pair_hashed = common.hashing_encoder(cols, n_components, df_pairs_dataset)
    i_dim = len(df_pair_hashed.columns)
    print(f"i_dim={i_dim}")

    # **  STEP 3 **
    # Fit the dataset to isotree - IsolationForestIsoTree
    # call to train or load saved model with the hashed data set
    model = train_isotree_model.load_save_isotree_if_model(df_pair_hashed, ds_name, i_dim, is_imputer, cols,
                                                           n_components, use_full_data, use_existing_model,
                                                           model_for, model_path)
    # **  STEP 4 **
    # predict the probability of anomaly of given dataset, returns a score of prediction
    # No need to change the below statement as it is generic
    print("Start prediction with decision_function...")
    predictions = model.decision_function(df_pair_hashed)
    set_type = "specific datapoints"
    if use_full_data == "Y":
        set_type = "full dataset"
    print(f"{model_for} isotree isolation forest, data prediction for {set_type} of the column pair completed")

    # **  STEP 5 **
    # Create dataframe from predictions & generate is_anomaly column based on threshold
    df_preds = pd.DataFrame(data=predictions, columns=['isotree_score'])

    # join the pairs of event with prediction
    result_df_preds = pd.concat([df_pairs_dataset, df_preds], axis=1)
    result_df_preds['is_isotree_anomaly'] = np.where(result_df_preds.isotree_score > threshold, 1, 0)

    # Return a dataframe with predictions
    return result_df_preds
