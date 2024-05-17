import json

import re
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

import draco_test
import pandas as pd
from collections import Counter
import time
import concurrent.futures
from environment import environment
import datetime
from StateGenerator import StateGenerator
from utils import run_algorithm
from zeng_app import perform_snd_flds
from performance import OnlineLearningSystem

port = 5500
rulesfile = './gvaemodel/rules-cfg.txt'
modelsave = './gvaemodel/vae_H256_D256_C444_333_L20_B200.hdf5'
m = re.search(r'_L(\d+)_', modelsave)

MAX_LEN = 20
LATENT = int(m.group(1))


visvae = None
pca = None

app = Flask(__name__)
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
    system.encode_history.append(field_names)
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

    system.encode_history.append(field_names)

    #write to a log file the selected recommendation for current session. can i get current session id?

    with open('selected_recommendation.txt', 'a') as f:
       #write field names and time
       time= datetime.datetime.now()
       f.write(f'{field_names} {time}\n')

    return jsonify(specs)







@app.route('/top_k', methods=['POST'])
def top_k(save_csv=False):
    print('Starting Recommendation Engine...')
    #get running time in console
    start_time = time.time()

    total_data = request.get_json()
    data = eval(total_data.get('history'))

    bookmarked_charts = total_data.get('bookmarked', [])
    specified_algorithm = total_data.get('algorithm', 'Qlearning')

    if data and isinstance(data, list):
        attributesHistory = data
    else:
        attributesHistory = [['flight_data', 'wildlife_size'], ['flight_data', 'wildlife_size', 'airport_name'],
                         ['flight_data', 'wildlife_size', 'airport_name']]

    print('Attribute History', attributesHistory)
    attributes,distribution_map,baselines_distribution_maps=system.onlinelearning(attributesHistory, algorithms_to_run=['Momentum','Random','Greedy','Qlearning'], specified_algorithm=specified_algorithm)

    print('Requesting Encodings...', '--- %s seconds ---' % (time.time() - start_time), 'Algorithm:', specified_algorithm)

    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom=system.remove_irrelevant_recommendations(attributes, recommendations, max_constrained=False)
    print(' Recommendations Finished...', "--- %s seconds ---" % (time.time() - start_time))
    print('Recommendation Size:', len(chart_recom))

    response_data = {
        "chart_recommendations": chart_recom,
        "distribution_map": distribution_map
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

