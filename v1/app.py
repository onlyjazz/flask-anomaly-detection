import os, sys
import logging
import json
from flask import Flask, request, Response, jsonify
import settings
from werkzeug.exceptions import HTTPException

app = Flask(__name__)  # Create a Flask WSGI application

# For PRODUCTION build
app.config["DEBUG"] = False  # set DEBUG = False for PROD build

sys.path.insert(0, 'models')

from api.models import get_missing_value_reports as gmr
from api.models import race_and_ethnic_bias as reb
from api.models import anomaly_detection as ad
from api.models import common


log = logging.getLogger(__name__)

SERVICES_HOME = os.path.dirname(os.path.realpath(__file__))
API_HOME = os.path.dirname(SERVICES_HOME)
upload_path = '{}/assets/reports/'.format(API_HOME)
app.config['upload_path'] = upload_path
model_base_path = '{}/models/$'.format(API_HOME)
app.config['model_base_path'] = model_base_path


@app.route("/healthcheck", methods=['GET'])
def home():
    """
        Endpoint: This healthcheck end point is just basic, can be customized to do more,
        if nee be.
    """
    results = {"status": "200", "message": "Healthcheck flaskdata_api is good"}
    json_result = common.format_parsed_json(results)
    return json_result


@app.route('/anomaly/missing_values', methods=['GET'])
def get_anomaly_missing_values_report():
    """
        Endpoint: Missing values (anomaly - level 1) report
    """
    try:
        # fetch inputs
        in_data = request.get_json()
        dataset_name = in_data["dataset_name"]
        save_plot = in_data["save_plot"]

        app.logger.info(app.config['upload_path'])
        # call to fetch missing value reports for a specific dataset_name
        df_result = gmr.get_missing_value_reports(dataset_name, upload_path, save_plot)

        # get formatted result
        json_result = common.format_json_to_rows(df_result)
    except HTTPException as he:
        message = "HTTPException Error occurred"
        json_result = Response(message, status=400, mimetype='application/json')
    except Exception as ex:
        inputs = "dataset_name, save_plot"
        message = f"Error occurred. Check your input list has {inputs} and try again."
        json_result = Response(message, status=500, mimetype='application/json')
    return json_result


@app.route('/anomaly/ethnic_racial_bias', methods=['GET'])
def get_ethnic_racial_bias_report():
    """
        Endpoint: Ethnic and racial bias report
    """
    params = []
    try:
        # fetch inputs
        in_data = request.get_json()
        dataset_name = in_data["dataset_name"]
        pair_data = in_data["pair_data"]
        show_columns = in_data["show_columns"]
        target_group = in_data["target_group"]
        save_plot = in_data["save_plot"]

        app.logger.info(app.config['upload_path'])
        # call to fetch missing value reports for a specific dataset_name
        df_result = reb.find_bias_score(dataset_name, pair_data, target_group, upload_path,
                                        save_plot, show_columns)

        # get formatted result
        result = ""
        if not df_result.empty:
            result = common.format_json_to_rows(df_result)
        params.append({"dataset": dataset_name, "pair_data": pair_data})
        json_result = Response(result, status=200, mimetype='application/json')
    except HTTPException as he:
        message = "HTTPException Error occurred"
        json_result = Response(message, status=400, mimetype='application/json')
    except Exception as ex:
        inputs = "dataset_name, pair_data, show_columns, target_group, save_plot"
        message = f"Error occurred. Check your input list has {inputs} and try again."
        json_result = Response(message, status=500, mimetype='application/json')
    return json_result


@app.route('/anomaly/anomaly_detection', methods=['GET'])
def get_anomaly_detection_isotree_if_report():
    """
        Endpoint: Anomaly detection for a column pair - datapoints or
        all datapoints for the columns
    """
    try:
        # fetch inputs
        in_data = request.get_json()
        ds_name = in_data["dataset_name"]
        print (ds_name)
        pair_data = in_data["pair_data"]

        use_full_data = in_data["use_full_data"]
        use_existing_model = in_data["use_existing_model"]
        model_for = in_data["model_name"]
        if "threshold" not in in_data:
            threshold = 0.5
        else:
            threshold = in_data["threshold"]

        # NOTE: About the param n_components - used in category_encoders HashingEncoder.
        # n_components: is how many bits to represent the feature
        # Categorical data can pose a serious problem when there are too many
        # unique values in the data set. So then, use high cardinality
        # of 32 bits per feature...
        
        if "n_components" not in in_data:
            n_components = 32
        else:
            n_components = in_data["n_components"]

        model_path = model_base_path.replace("$", "isotree")
        print(model_path)

        app.config['model_path'] = model_path
        app.logger.info(app.config['model_path'])
        # call to fetch data anomalies for the passed data points
        df_result = ad.get_anomaly_isotree(pair_data, ds_name, use_full_data, use_existing_model,
                                           model_for, model_path, threshold, n_components)

        # get formatted result
        json_result = common.format_json_to_rows(df_result)
    except HTTPException as he:
        message = "HTTPException Error occurred"
        json_result = Response(message, status=400, mimetype='application/json')
    except Exception as ex:
        inputs = "dataset_name, pair_data, threshold, use_full_data, use_existing_model, model_name"
        message = f"Error occurred. Check your input list has {inputs} and try again."
        json_result = Response(message, status=500, mimetype='application/json')
    return json_result


def main():
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
