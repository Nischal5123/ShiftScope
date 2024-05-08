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

#encode history
encode_history = []

# memory for all algorithms history
momentum_attributes_history = []
greedy_attributes_history = []
random_attributes_history = []
rl_attributes_history = []

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
    encode_history.append(field_names)
    # Get Draco recommendations
    recommendations = draco_test.get_draco_recommendations(field_names, 'birdstrikes', parsed_data)
    # matched_recommendations = []
    #
    # # Initialize variables to track the maximum number of matched fields and the corresponding recommendation
    # max_match = 0
    # max_match_recommendation = None
    #
    # # Iterate over the recommendations and check for matches
    # for chart_key, chart in recommendations.items():
    #     encodings = json.loads(chart).get('encoding', {})
    #     matched_fields = 0
    #
    #     # Compare each field in the recommendation with the parsed data
    #     for field, field_info in encodings.items():
    #         if field in field_names and field_info.get('field') == field and field_types[field] == field_info.get(
    #                 'type'):
    #             matched_fields += 1
    #
    #     # Update the maximum match and corresponding recommendation if a new maximum is found
    #     if matched_fields > max_match:
    #         max_match = matched_fields
    #         max_match_recommendation = chart
    #
    # # If there is a recommendation with a match, add it to the list of matched recommendations
    # if max_match_recommendation:
    #     matched_recommendations.append(max_match_recommendation)
    #
    # if len(matched_recommendations) == 0:
    #     matched_recommendations.append(recommendations[0])
    chart_recom=remove_irrelevant_reccomendations(field_names, recommendations)
    return jsonify(chart_recom[0])




@app.route('/get-fields', methods=['POST'])
def encode_test():
    specs = request.get_json()
    # print(specs)
    parsed_data = [json.loads(item) for item in specs]

    # Extract field names from the parsed JSON
    field_names = []
    for item in parsed_data:
        # Assuming 'encoding' contains the fields and is structured consistently as shown in your sample
        encodings = item.get('encoding', {})
        for key in encodings:
            field_info = encodings[key]
            field_name = field_info.get('field')
            if field_name:
                field_names.append(field_name)
    return jsonify(field_names)

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

    encode_history.append(field_names)

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
    attributes,distribution_map,baselines_distribution_maps=onlinelearning(attributesHistory, algorithms_to_run=['Momentum','Random','Greedy','Qlearning'], specified_algorithm=specified_algorithm)

    print('Requesting Encodings...', '--- %s seconds ---' % (time.time() - start_time), 'Algorithm:', specified_algorithm)
    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom=remove_irrelevant_reccomendations(attributes, recommendations)
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





@app.route('/get-performance-data', methods=['GET'])
def read_json_file(file_path='distribution_map.json', algorithms=['Momentum','Random','Greedy']):
    with open(file_path, 'r') as file:
        data = json.load(file)

    #for each algo get it from the file
    baselines_distribution_maps = {}
    for algo in algorithms:
        with open(f'{algo}_distribution_map.json', 'r') as f:
            baselines_distribution_maps[algo] = json.load(f)


    response_data = {
        "distribution_map": data,
        "baselines_distribution_maps": baselines_distribution_maps
    }

    return jsonify(response_data)



def remove_irrelevant_reccomendations(interested_attributes, recommendations, max_constrained=True):
    fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date',
                  'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size',
                  'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a',
                  'speed_ias_in_knots']
    chart_recom = []
    chart_all = []
    for chart_key, _ in recommendations.items():
        chart = recommendations[chart_key]
        chart_all.append(chart)
        encodings = json.loads(chart).get('encoding', {})
        match = 0

        if  max_constrained:
            for field in fieldnames:
                if field in str(encodings):
                    match += 1
            if match == len(interested_attributes):
                chart_recom.append(chart)
        else:
            for f in interested_attributes:
                if f in str(encodings):
                    match += 1
                else:
                    match -= 1
            if match > 0:
                chart_recom.append(chart)

    if len(chart_recom) == 0:
        return chart_all[:1] # Need to return something to avoid empty response
    else:
        return chart_recom


def get_distribution_of_states(data, dataset='birdstrikes'):
    """
    Get the distribution of states in the data.

    Args:
    - data (pd.DataFrame): the data to analyze.

    Returns:
    - distribution (dict): a dictionary containing the probability of states.
    """
    # Define the list of all possible field names and convert them to lowercase
    if dataset == 'birdstrikes':
        fieldnames = ['airport_name', 'aircraft_make_model', 'effect_amount_of_damage', 'flight_date', 'aircraft_airline_operator', 'origin_state', 'when_phase_of_flight', 'wildlife_size', 'wildlife_species', 'when_time_of_day', 'cost_other', 'cost_repair', 'cost_total_a', 'speed_ias_in_knots']

    # Create a Counter with all possible field names
    distribution = Counter({key: 0 for key in fieldnames})

    # Count the frequency of field names in the data
    for state_list in data['State']:
        for state in state_list:
            if state.lower() in distribution:
                distribution[state.lower()] += 1

    # Calculate the total count of states, small epsilon added to avoid division by zero
    total = sum(distribution.values())+0.000000000000001

    # Normalize the counts to obtain probabilities
    distribution = {key: count / total for key, count in distribution.items()}

    return distribution



def onlinelearning(attributesHistory, algorithms_to_run=['Momentum','Random','Greedy','Qlearning'], dataset='birdstrikes', specified_algorithm='Qlearning'):
    """
    Online learning algorithm to predict the next state of the environment.
    Args:
        attributesHistory:
        algorithm:

    Returns:

    """

    generator = StateGenerator(dataset)

    #make the array as a pandas dataframe with index and whole attribute as a State column
    df = pd.DataFrame({'State': attributesHistory})

    distribution_map=get_distribution_of_states(df)


    #df_with_actions = process_actions(df)

    # Create a ThreadPoolExecutor with a maximum of 4 workers (adjust as needed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit each algorithm to the executor and get the results
        futures = {executor.submit(run_algorithm, algorithm, attributesHistory, generator, dataset): algorithm for algorithm in
                   algorithms_to_run}
        results = {futures[future]: future.result() for future in concurrent.futures.as_completed(futures)}

    # Extract the results for each algorithm
    next_state_rl = results['Qlearning']
    next_state_momentum = results['Momentum']
    next_state_greedy = results['Greedy']
    next_state_random = results['Random']

    #get result based on the specified algorithm
    if specified_algorithm :
        next_state_return = results[specified_algorithm]


    # Append the results to their respective attribute histories
    momentum_attributes_history.append(next_state_momentum)
    greedy_attributes_history.append(next_state_greedy)
    random_attributes_history.append(next_state_random)
    rl_attributes_history.append(next_state_rl)

    #save these to a numpy file in /data folder
    path='performance-data/'
    for i in range(len(attributesHistory)):
        if len(attributesHistory[i]) < 3:
            attributesHistory[i].extend(['none'] * (3 - len(attributesHistory[i])))
    np.save(path+'user_attributes_history.npy', attributesHistory)


    for i in range(len(momentum_attributes_history)):
        if len(momentum_attributes_history[i]) < 3:
            momentum_attributes_history[i].extend(['none'] * (3 - len(momentum_attributes_history[i])))
    np.save(path+'momentum_attributes_history.npy', momentum_attributes_history)

    for i in range(len(greedy_attributes_history)):
        if len(greedy_attributes_history[i]) < 3:
            greedy_attributes_history[i].extend(['none'] * (3 - len(greedy_attributes_history[i])))
    np.save(path+'greedy_attributes_history.npy', greedy_attributes_history)

    for i in range(len(random_attributes_history)):
        if len(random_attributes_history[i]) < 3:
            random_attributes_history[i].extend(['none'] * (3 - len(random_attributes_history[i])))
    np.save(path+'random_attributes_history.npy', random_attributes_history)

    for i in range(len(rl_attributes_history)):
        if len(rl_attributes_history[i]) < 3:
            rl_attributes_history[i].extend(['none'] * (3 - len(rl_attributes_history[i])))
    np.save(path+'rl_attributes_history.npy', rl_attributes_history)


    # Construct DataFrames and distribution maps for each algorithm
    df_momentum = pd.DataFrame({'State': momentum_attributes_history})
    distribution_map_momentum = get_distribution_of_states(df_momentum)

    df_greedy = pd.DataFrame({'State': greedy_attributes_history})
    distribution_map_greedy = get_distribution_of_states(df_greedy)

    df_random = pd.DataFrame({'State': random_attributes_history})
    distribution_map_random = get_distribution_of_states(df_random)

    df_rl = pd.DataFrame({'State': rl_attributes_history})
    distribution_map_rl = get_distribution_of_states(df_rl)

    # Construct a dictionary containing distribution maps for all algorithms
    all_algorithms_distribution_map = {
        'Momentum': distribution_map_momentum,
        'Greedy': distribution_map_rl,  # Let's send this as Greedy for now
        'Random': distribution_map_random
    }

    return next_state_return, distribution_map, all_algorithms_distribution_map




def process_actions(data):
    # print("Converting '{}'...".format(csv_filename))

    df = data
    actions = []

    for index in range(len(df) - 1):
        current_state = np.array(df['State'][index] ) # Convert string representation to list
        next_state = np.array(df['State'][index + 1] ) # Convert string representation to list

        # Count occurrences of each element in current_state and next_state
        current_state_count = Counter(current_state)
        next_state_count = Counter(next_state)

        # Get the elements that are in next_state but not in current_state
        difference_elements = list((next_state_count - current_state_count).elements())

        # Get the number of different elements
        num_different_elements = len(difference_elements)

        if num_different_elements == 0:
            action = 'same'
        else:
            action = f'modify-{num_different_elements}'


        actions.append(action)

    actions.append('none')  # This is the action we want to predict
    df['Action'] = actions

    return df

if __name__ == '__main__':
    # attributesHistory= [['flight_data','wildlife_size'],['flight_data','wildlife_size','airport_name'],['flight_data','wildlife_size','airport_name']]
    # onlinelearning(attributesHistory)
    # top_k()
    app.run(port=port, debug=False)
