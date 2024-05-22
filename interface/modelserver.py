import json

import re
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory, current_app
from flask_cors import CORS

import draco_test
import pandas as pd
from collections import Counter
import time
import concurrent.futures
from environment import environment
import datetime
from StateGenerator import StateGenerator
from zeng_app import perform_snd_flds
from performance import OnlineLearningSystem
import pdb
import concurrent.futures

port = 5500

MAX_LEN = 20

app = Flask(__name__, static_folder='web/static',
            template_folder='web/templates')
CORS(app)

env = environment()

system = OnlineLearningSystem()

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/encode', methods=['POST'])
def encode():
    specs = request.get_json()
    parsed_data = [json.loads(item) for item in specs]

    # Extract field names and types from the parsed JSON
    field_names = []
    encoding_channels = []
    field_types = {}
    for item in parsed_data:
        marks = [item.get('mark', 'bar')]
        encodings = item.get('encoding', {})
        for key in encodings:
            encoding_channels.append(key)
            field_info = encodings[key]
            field_name = field_info.get('field')
            if field_name:
                field_names.append(field_name)
                field_types[field_name] = key
    system.response_history.append(field_names)
    # Get Draco recommendations
    recommendations = draco_test.get_draco_recommendations(field_names, 'birdstrikes', parsed_data)
    chart_recom=system.remove_irrelevant_recommendations(field_names, recommendations)
    return jsonify(chart_recom[0])


@app.route('/get-performance-data', methods=['GET'])
def read_json_file(file_path='distribution_map.json', algorithms=['Momentum','Random','Greedy']):
    response=system.read_json_file(algorithms)

    return response


#This is to get the recommendation that the user has selected
@app.route('/encode2', methods=['POST'])
def encode2():
    specs = request.get_json()
    parsed_data = json.loads(specs)

    # Extract field names from the parsed JSON
    field_names = []
    parsed_data.get('encoding', {})
    if parsed_data.get('encoding', {})!= {}:
        encodings = parsed_data.get('encoding', {})
    elif parsed_data.get('spec', {}).get('encoding', {}) != {}:
        encodings = parsed_data.get('spec', {}).get('encoding', {})
    else:
        encodings = {}
    for key in encodings:
        field_info = encodings[key]
        field_name = field_info.get('field')
        if field_name:
            field_names.append(field_name)

    system.response_history.append(field_names)
    system.update_models()
    #write to a log file the selected recommendation for current session. can i get current session id?

    with open('selected_recommendation.txt', 'a') as f:
       #write field names and time
       time= datetime.datetime.now()
       f.write(f'{field_names} {time}\n')

    return jsonify(specs)

def recommendation_generation(attributes):
    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom= system.remove_irrelevant_recommendations(attributes, recommendations, max_constrained=False)
    return chart_recom

@app.route('/top_k', methods=['POST'])
def top_k(save_csv=False):
    print('Starting Recommendation Engine...')
    #get running time in console
    start_time = time.time()

    total_data = request.get_json()
    data = eval(total_data.get('history'))

    bookmarked_charts = total_data.get('bookmarked', [])
    specified_algorithm = total_data.get('algorithm', 'ActorCritic')

    if data and isinstance(data, list):
        system.state_history = data
    else:
        system.state_history = [['flight_date', 'wildlife_size'], ['flight_date', 'wildlife_size', 'airport_name'],
                         ['flight_date', 'wildlife_size', 'airport_name']]

    # print('Attribute History', attributesHistory)
    attributes_list,distribution_map,baselines_distribution_maps, attributes_baseline=system.onlinelearning(algorithms_to_run=['Momentum','Random','Greedy','ActorCritic'])

    # print('Requesting Encodings...', '--- %s seconds ---' % (time.time() - start_time), 'Algorithm:', specified_algorithm)
    # print(len(attributes_list))
    chart_recom_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        future_to_attributes = {executor.submit(recommendation_generation, attributes): attributes for attributes in attributes_list}
        for future in concurrent.futures.as_completed(future_to_attributes):
            chart_recom = future.result()
            chart_recom_list.extend(chart_recom)

        # pdb.set_trace()
    print(' Recommendations Finished...', "--- %s seconds ---" % (time.time() - start_time))
    # print('Recommendation Size:', len(chart_recom))

    print('Requesting Encodings...', '--- %s seconds ---' % (time.time() - start_time), 'Algorithm:', 'Momentum')
    #now for baseline algorithm
    baseline_recommendations = draco_test.get_draco_recommendations(attributes_baseline)
    baseline_chart_recom = system.remove_irrelevant_recommendations(attributes_baseline, baseline_recommendations, max_constrained=False)
    print(' Basline Recommendations Finished...', "--- %s seconds ---" % (time.time() - start_time))

    response_data = {
        "chart_recommendations": chart_recom_list,
        "distribution_map": distribution_map,
        "baseline_chart_recommendations": baseline_chart_recom,
    }

    for algo, base_distribution_map in baselines_distribution_maps.items():
        with open(f'{algo}_distribution_map.json', 'w') as f:
            json.dump(base_distribution_map, f)

    with open('distribution_map.json', 'w') as file:
        json.dump(distribution_map, file)

    if save_csv:
        distribution_map_dataframe = pd.DataFrame.from_dict(distribution_map, orient='index', columns=['Probability'])
        distribution_map_dataframe.index.name = 'Fields'
        pd.DataFrame.to_csv(distribution_map_dataframe, 'distribution_map.csv')

    return jsonify(response_data)


if __name__ == '__main__':
    # attributesHistory= [['flight_data','wildlife_size'],['flight_data','wildlife_size','airport_name'],['flight_data','wildlife_size','airport_name']]
    # onlinelearning(attributesHistory)
    # top_k()
    app.run(port=port, debug=False)
