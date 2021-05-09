# Import libraries
import os
from isotree import IsolationForest as IsolationForestIsoTree
from api.models import common


def load_save_isotree_if_model(df_data, ds_name, i_dim, is_imputer, cols, n_components,
                               use_full_data, use_existing_model, model_for, model_path):
    """
        Description: get anomaly detection on column pair dataset using
                            isotree - IsolationForest

        :param df_data:
        :param ds_name:
        :param i_dim:
        :param is_imputer:
        :param cols:
        :param n_components:
        :param use_full_data:
        :param use_existing_model:
        :param model_for:
        :param model_path:
        :return: isotree model

    """

    model = None
    model_exists = False

    model_prefix = ""
    if use_full_data == "Y":
        model_prefix = "_full"
    else:
        model_prefix = '_'.join(map(str, cols))

    # path to the stored iso-tree model
    model_filename = f"model_isotree_{model_for}{model_prefix}.pkl"
    model_filename = os.path.join(model_path, model_filename)
    model_path_filename = os.path.join('./models/isotree/', model_filename)
    if use_existing_model == 'Y':
        model = common.load_model(model_path_filename)
        print('Load Existing Model...')
    else:
        print('Train New Model...')
        if use_full_data == "N":
            # When using a subset of data points for the column pair - make
            # sure to train for all the data points first and then predict for the
            # subset of data points
            # print(f"col: {cols}")
            df_pair = common.get_data_for_cols(cols, ds_name)
            df_hashed = common.hashing_encoder(cols, n_components, df_pair)
            i_dim_N = len(df_hashed.columns)
            print(f"i_dim_N={i_dim_N}")
            model = IsolationForestIsoTree(ndim=i_dim
                                           , ntrees=100
                                           , penalize_range=False
                                           , ntry=10
                                           , prob_pick_pooled_gain=0
                                           , build_imputer=is_imputer)
            model.fit(df_hashed)
            common.save_model(model, model_path_filename)
            print(f"{model_for} isotree model saved as '{model_filename}'")
        else:
            model = IsolationForestIsoTree(ndim=i_dim
                                           , ntrees=100
                                           , penalize_range=False
                                           , ntry=10
                                           , prob_pick_pooled_gain=0
                                           , build_imputer=is_imputer)
            model.fit(df_data)
            common.save_model(model, model_path_filename)
            print(f"{model_for} isotree model saved as '{model_filename}'")

    return model
