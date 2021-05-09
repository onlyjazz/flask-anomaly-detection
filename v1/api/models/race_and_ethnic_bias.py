# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
import sys
warnings.filterwarnings('ignore')

from smclarify.bias.report import *
from matplotlib.backends.backend_pdf import PdfPages
from api.services import flaskdata_superset
from api.models import common

# add paths to sys
sys.path.insert(0, 'models')
sys.path.insert(1, 'assets/reports')


# ********************* Start of FUNCTIONS USED FOR PROCESSING: *****************************
def race_and_country_plots(df, columns, target_group, rep_path):
    """
        Create plots for race against country to show the bias and save if need be
        :param df:
        :param columns:
        :param target_group:
        :param rep_path:
    """
    df_sub = df[columns]
    # race = pd.value_counts(df_sub['RACEN'].values, sort=True)
    race = pd.value_counts(df_sub['RACECD'].values, sort=True)
    country = pd.value_counts(df_sub[target_group].values, sort=True)

    # create pdf for the file_path
    file_path = os.path.join(rep_path, "race_and_country_plots.pdf")
    pdf = PdfPages(file_path)

    # plot and save race distribution
    race_fig = plt.figure(figsize=(10, 5))
    plt.title('Race distribution')
    plt.xlabel('Race Code')
    plt.ylabel('Values')
    race_plot = sns.barplot(race.index, race.values, alpha=0.8)
    pdf.savefig(race_fig)

    # plot and save country distribution
    country_fig = plt.figure(figsize=(10, 5))
    plt.title('Country distribution')
    plt.xlabel('Country Code')
    plt.ylabel('Values')
    country_plot = sns.barplot(country.index, country.values, alpha=0.8)
    pdf.savefig(country_fig)

    pdf.close()


# **** HELPER FUNCTIONS: **************************************************************
def preprocess_data(df):
    """
    Pro-process and convert dataset into algorithm ready format (numerical values)
    :param df:

    INPUT :
        (pandas.DataFrame) Dataframe
    OUTPUT:
        (pandas.DataFrame) Dataframe
    """

    # **************************************************************************************
    # *** NOTE: These columns can be tweaked as a parameter from api call if need be
    cols_to_drop = ['BRTHDTC', 'ATPSYFL', 'RACESP', 'EXCLREAS', 'TRTSDTM', 'TRTEDTM', 'DFIU', 'DEATHDTC', 'DFIU',
                    'EXCLREAN', 'CONMTH', 'DEATHDT', 'DTHCAUS', 'DTHCGR1', 'ACTDT', 'DFI']
    # **************************************************************************************

    df_new = df.drop(cols_to_drop, axis=1)
    df_new = df_new.dropna(how='any')
    return df_new


def measure_bias_in_attribute(df, primary_col, target_col, target_pos_val, group_col):
    """
    Measure Bias in Data Based on Primary Column with Target Column which is grouped by Grouping Column
    :param df:
    :param primary_col:
    :param target_col:
    :param target_pos_val:
    :param group_col:

    INPUTS :
        (pandas.DataFrame) Dataframe
        (str) primary_col, target_col, target_pos_val, group_col
    OUTPUT :
        (list) A Summary Report containing various statistics about the data using the defined grouping
    """
    # Measure bias for an attribute
    facet_column = FacetColumn(primary_col)
    label_column = LabelColumn(name=target_col, data=df[target_col], positive_label_values=[target_pos_val])

    if group_col in df.columns:
        group_variable = df[group_col]
        report = bias_report(df, facet_column, label_column, stage_type=StageType.PRE_TRAINING,
                             group_variable=[group_variable])
    else:
        report = bias_report(df, facet_column, label_column, stage_type=StageType.PRE_TRAINING)

    return report


def get_reports(df, primary_col, target_column_values, target_group):
    """
    Get reports for target columns as a list
    :param df:
    :param primary_col:
    :param target_column_values:
    :param target_group:

    INPUT :
        (pandas.DataFrame) Dataframe
        (str) primary_col, cols_of_interest :list of columns of interest
    OUTPUT:
        list of reports
    """
    reports_list = []
    report_cat_list = []

    for (target_key, target_key_vals) in target_column_values:
        target_key_vals = iter(target_key_vals)
        exists = True
        while exists:
            target_value = next(target_key_vals, 'end')
            if target_value == 'end':
                break
            else:
                # print(f"key: {target_key}, value: {val}")
                report = measure_bias_in_attribute(df,
                                                   primary_col=primary_col,
                                                   target_col=target_key,
                                                   target_pos_val=target_value,
                                                   group_col=target_group)
                report_cat_list.append(report)
        reports_list.append(report_cat_list)
        report_cat_list = []
    return reports_list


def get_bias_scores(reports, target_values):
    """
    Returns the aggregated bias score
    :param reports:
    :param target_values:
    INPUT :
        (pandas.DataFrame) Dataframe
        (list) report, list of target values

    OUTPUT:
        (dict) bias scores
    """
    scores_dict = dict.fromkeys(target_values)
    for j in range(len(reports)):
        scores = []
        report = reports[j]
        for i in range(len(report)):
            target = report[i]['value_or_threshold']  # WHITE
            ci = report[i]['metrics'][1]['value']
            dpl = report[i]['metrics'][2]['value']
            # ci = abs(ci)
            if ci < 0.0:
                ci = abs(ci)
            else:
                ci = 1.0 - ci
            dpl = 1.0 - abs(dpl)

            scores.append({"value": target, "score": (2 * ci + 1 * dpl) / 3})
        scores_dict[target_values[j]] = scores

    return scores_dict


def allocate_scores(df, target, target_value_dict, feature):
    """
        Allots bias score based to respective samples based on the primary and target feature values
        :param df:
        :param target:
        :param target_value_dict:
        :param feature:
    """
    col_name = f"{target}_B"
    df[col_name] = 0.0

    for target_val in target_value_dict.keys():
        for attr_value in target_value_dict[target_val]:
            value = attr_value['value']
            score = attr_value['score']
            df.loc[((df[target] == target_val) * (df[feature] == value)), col_name] = score

    return df[col_name].values


def find_bias_score(ds_name, pair_data, target_group, save_folder,
                    save_plot="N", show_columns=""):
    """
      Main function to calculate BIAS
      :param ds_name:
      :param pair_data:
      :param target_group:
      :param save_folder:
      :param save_plot:
      :param show_columns:
    """
    # Download data from flaskdata
    df_data = flaskdata_superset.get_data(ds_name)

    # Preprocess the dataset
    df = preprocess_data(df_data)

    # extract Target Columns and Values
    target_columns, target_values, target_columns_values = common.get_key_and_values(pair_data)
    target_col1 = target_columns[0]
    target_col2 = target_columns[1]

    col_1_values = target_values[0]
    col_2_values = target_values[1]

    # Get reports for given target keys and target thresholds
    race_reports = get_reports(df, "RACE", target_columns_values, target_group)
    ethnicity_reports = get_reports(df, "ETHNIC", target_columns_values, target_group)

    # Get Racial Bias Scores
    # For column 1 in the pair_data
    race_scores_death = get_bias_scores(race_reports[0], col_1_values)
    race_bias_scores_death = allocate_scores(df, target_col1, race_scores_death, "RACE")

    # For column 2 in the pair_data
    race_scores_age = get_bias_scores(race_reports[1], col_2_values)
    race_bias_scores_age = allocate_scores(df, target_col2, race_scores_age, "RACE")
    racial_bias_scores = (race_bias_scores_death + race_bias_scores_age) / 2

    # Get Ethnicity Bias Scores
    # For column 1 in the pair_data
    ethnic_scores_death = get_bias_scores(ethnicity_reports[0], col_1_values)
    ethnic_bias_scores_death = allocate_scores(df, target_col1, ethnic_scores_death, "ETHNIC")

    # For column 2 in the pair_data
    ethnic_scores_age = get_bias_scores(ethnicity_reports[1], col_2_values)
    ethnic_bias_scores_age = allocate_scores(df, target_col2, ethnic_scores_age, "ETHNIC")

    # Mean ethnicity bias scores
    ethnicity_bias_scores = (ethnic_bias_scores_death + ethnic_bias_scores_age) / 2

    # Combine to get final bias score
    df['BIAS'] = (racial_bias_scores + ethnicity_bias_scores) / 2
    # Uncomment to save csv file
    # bias_path = "bias"
    # bias_report_filename = os.path.join(save_folder, bias_path, f"{ds_name}_bias.csv")
    # df.to_csv(bias_report_filename, index = False)

    # save plot if save_plot = "Y"
    if save_plot == "Y":
        bias_path = "bias"
        rep_path = os.path.join(save_folder, bias_path)
        cols = df_data.columns
        # if no columns are specified for the report then set default columns
        if show_columns == "":
            # Use 'RACECD' instead of 'RACEN'
            show_columns = ['SUBJID', 'SITEID', 'INVID', 'COUNTRY', 'RACECD', 'AGEIC', 'AGEGR1N', 'AGEGR2N', 'DFI', 'GEOREGN']
        race_and_country_plots(df_data, show_columns, target_group, rep_path)

    # Returning bias scores as a pandas dataframe
    return df
