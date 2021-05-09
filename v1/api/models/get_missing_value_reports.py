# Import libraries and tools
import os
import sys

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import seaborn as sns
import logging
from api.services import flaskdata_superset

# add paths to sys
sys.path.insert(0, 'models')
sys.path.insert(1, 'assets/reports')

# ************************************************************************************
# NOTE: Use
# matplotlib.use('Agg')
#  -- in order to start matplotlib, on its own backend, so we can avoid the warning:
# UserWarning: Starting a Matplotlib GUI outside of the main thread will likely fail.
#               fig, ax = plt.subplots(1, 1, dpi=200)
matplotlib.use('Agg')
# ************************************************************************************

log = logging.getLogger(__name__)


def get_missing_values_count(df):
    """
        Takes in a dataframe and generates a new dataframe that contains the count and
        percentage of missing values for each variable
        :param df: a pandas dataframe
        :return: a dataframe
    """
    missing_values = df.isnull().sum()
    mv_percent = round(df.isnull().mean().mul(100), 2)
    mv_table = pd.concat([missing_values, mv_percent], axis=1)
    mv_table = mv_table.rename(
        columns={df.index.name: 'Column', 0: 'Missing_Values', 1: 'Pct_Total_Missing_Values'})
    mv_table = mv_table[mv_table.iloc[:, 1] != 0].sort_values('Pct_Total_Missing_Values', ascending=False)
    return mv_table


def visualize_missing_values_table(mv_table, ds_name, rep_path, save_plot):
    """
        Takes in a dataframe and generates a plot of the missing values table
        :param mv_table:
        :param ds_name:
        :param rep_path:
        :param save_plot:
    """

    if save_plot != 'V':
        # Turn off the interactive mode
        plt.ioff()
    try:
        scaled = mv_table.copy()
        scaled['Missing_Values'] = 100 * scaled['Missing_Values'] / (scaled['Missing_Values'].max())
        fig, ax = plt.subplots(1, 1, dpi=200, figsize=(5, 10))
        ax = sns.heatmap(scaled, annot=mv_table, fmt='.0f', cbar=False, cmap='Reds', vmin=0, vmax=100)
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        ax.tick_params(left=False, top=False)
        ax.set_title(f'Table of Missing Values Counts and Percentages - ({ds_name})')

        if save_plot == 'V':
            # View ONLY
            plt.show()
        else:
            if save_plot == 'S':
                # save plot as a pdf
                plt_filename = os.path.join(rep_path, f"missing_values_table_{ds_name}.pdf")
                plt.savefig(plt_filename, format='pdf', bbox_inches='tight')

            plt.close(fig)
    except Exception as e:
        log.info(f"Missing Values Table Error: {e}")


def visualize_missing_ness_correlation(df, ds_name, rep_path, save_plot):
    """
        Takes in a dataframe and generates a plot that shows the correlation
        of the missing data
        :param df:
        :param ds_name:
        :param rep_path:
        :param save_plot:
    """

    if save_plot != 'V':
        # Turn off the interactive mode
        plt.ioff()
    try:
        fig, ax = plt.subplots(1, 1, dpi=200);
        columns_with_missing_values = df.columns[df.isnull().any()]
        if len(columns_with_missing_values) > 30:
            ax.set_title(f'Heatmap of Missing Values Correlation Between 30 Randomly Selected Variables - ({ds_name})', fontsize=8)
            df = df[columns_with_missing_values].sample(n=30, axis='columns')
        else:
            ax.set_title(f'Heatmap of Missing Values Correlation Between Variables - ({ds_name})', fontsize=8)
            df = df[columns_with_missing_values]
        corr_matrix = df.isnull().corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        font_size = 5 / (1 + len(corr_matrix) / 100)
        ax = sns.heatmap(corr_matrix, mask=mask, vmin=-1, vmax=1, xticklabels=1,
                         yticklabels=1, annot=True, fmt='.1f', annot_kws={"size": font_size},
                         cmap='coolwarm')
        cb_ax = fig.axes[1]
        cb_ax.tick_params(labelsize=font_size, length=3, width=1)
        ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=font_size, rotation='vertical')
        ax.set_yticklabels(ax.get_ymajorticklabels(), fontsize=font_size, rotation='horizontal')

        if save_plot == 'V':
            # View ONLY
            plt.show()
        else:
            if save_plot == 'S':
                # save plot as a pdf
                plt_filename = os.path.join(rep_path, f"missingness_correlation_{ds_name}.pdf")
                fig.savefig(plt_filename, format='pdf', bbox_inches='tight')
            plt.close()
    except Exception as e:
        print('Correlation Graph Error:', e)


def get_missing_value_count(row):
    """
        Takes in a dataframe row and finds the number of missing values in the row
        Returns the number of missing values as an int
        :param row:
        :return:
    """
    missing_value_count = row.isnull().sum()
    return missing_value_count


def visualize_missing_value_histogram(df, ds_name, rep_path, save_plot):
    """
        Takes in a dataframe and generates a histogram which shows the distribution of
        the number of missing values per row
        :param df:
        :param ds_name:
        :param rep_path:
        :param save_plot:
    """

    if save_plot != 'V':
        # Turn off the interactive mode
        plt.ioff()
    try:
        df['Missing_value_count'] = df.apply(get_missing_value_count, axis=1)
        fig, ax = plt.subplots(1, 1, dpi=200)
        ax = sns.histplot(df['Missing_value_count'], discrete=True)
        plt.xlabel('Number of Missing Values Per Row')
        ax.set_title(f'Histogram of Missing Value Count per Row - ({ds_name})')
        if save_plot == 'V':
            # View ONLY
            plt.show()
        else:
            if save_plot == 'S':
                # save plot as a pdf
                plt_filename = os.path.join(rep_path, f"missingness_histogram_{ds_name}.pdf")
                fig.savefig(plt_filename, format='pdf', bbox_inches='tight')
            plt.close()
    except Exception as e:
        log.info(f"Histogram Graph Error: {e}")


def get_missing_value_reports(ds_name, save_folder, save_plot="N"):
    """
        Main function to process all the missing value reports.
        :param ds_name:
        :param save_folder:
        :param save_plot:
    """
    df_amt_missing_data = None

    try:
        df = flaskdata_superset.get_data(ds_name)
        # Save visualizations
        df_amt_missing_data = get_missing_values_count(df)
        rep_path = ""

        # *******************************************************************
        # ***  NOTE: Possible values for the save_plot flag
        #            for now are:
        #            V - VIEW only
        #            S - SAVE only
        #            N - No action
        #      In all the above cases, the missing values data frame is
        #      returned as result
        # NOTE: You may change which missingness, you want to return as the
        #       the result (output)
        # *******************************************************************
        if save_plot == "S":
            missing_path = "missing"
            rep_path = os.path.join(save_folder, missing_path)

        # Visualizations start
        visualize_missing_values_table(df_amt_missing_data, ds_name, rep_path, save_plot)
        visualize_missing_ness_correlation(df, ds_name, rep_path, save_plot)
        visualize_missing_value_histogram(df, ds_name, rep_path, save_plot)

    except Exception as e:
        log.info(f"Dataset {ds_name} is not available. Error: {e}")

    return df_amt_missing_data
