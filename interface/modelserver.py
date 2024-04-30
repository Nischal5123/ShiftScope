import json
import os
import sys
import re
from multiprocessing import Pool
import nltk
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import procrustes

# import tensorflow as tf
# from tensorflow.keras import backend as K
# from sklearn.decomposition import PCA
# from sklearn.manifold import MDS, smacof
from flask import Flask, jsonify, request
from flask_cors import CORS
import pdb 
import draco_test
import pandas as pd
from collections import Counter
import time


# from gvaemodel.vis_vae import VisVAE, get_rules, get_specs
# from gvaemodel.vis_grammar import VisGrammar
from environment import environment
import datetime
from Momentum import Momentum
from StateGenerator import StateGenerator

port = 5500
rulesfile = './gvaemodel/rules-cfg.txt'
modelsave = './gvaemodel/vae_H256_D256_C444_333_L20_B200.hdf5'
m = re.search(r'_L(\d+)_', modelsave)

MAX_LEN = 20
LATENT = int(m.group(1))

# rules = []
# with open(rulesfile, 'r') as inputs:
#     for line in inputs:
#         line = line.strip()
#         rules.append(line)

# visvae = VisVAE(modelsave, rules, MAX_LEN, LATENT)
# graph = tf.get_default_graph()

# pca = PCA(n_components=2)

visvae = None
# graph = None
# sess = None
pca = None

app = Flask(__name__)
CORS(app)

env = environment()

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

    #get_draco recommendations
    recommendations = draco_test.get_draco_recommendations(field_names)
    chart_recom = []
    for chart_key, _ in recommendations.items():
        chart = recommendations[chart_key]
        encodings = json.loads(chart).get('encoding', {})
        match=0
        for f in field_names:
            if f in str(encodings):
                match+=1
        if match==len(field_names):
                chart_recom.append(chart)
    return jsonify(chart_recom[0])

# def check_fields(dictionary, fields):
#     for key, value in dictionary.items():
#         if isinstance(value, dict):
#             if not check_fields(value, fields):  # Modify this line
#                 return False  # Modify this line
#         elif key not in fields and value not in fields:  # Modify this line
#             return False
#     return True  # Modify this line
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

    #write to a log file the selected recommendation for current session. can i get current session id?

    with open('selected_recommendation.txt', 'a') as f:
       #write field names and time
       time= datetime.datetime.now()
       f.write(f'{field_names} {time}\n')




    return jsonify(specs)


@app.route('/top_k', methods=['POST'])
def top_k():
    print('Starting Recommendation Engine...')
    #get running time in console
    start_time = time.time()

    data = request.get_json()
    if data and isinstance(data, list):
        attributesHistory = data
    else:
        attributesHistory = [['flight_data', 'wildlife_size'], ['flight_data', 'wildlife_size', 'airport_name'],
                         ['flight_data', 'wildlife_size', 'airport_name']]
    print(attributesHistory)
    attributes=onlinelearning(attributesHistory, algorithm='Momentum')

    # #greedy always use the last 3 attributes
    # attributes=attributesHistory[-1]


    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom = []
    for chart_key, _ in recommendations.items():
        # (_,chart)=(recommendations[chart_key])
        chart = recommendations[chart_key]
        if len(chart_recom) < 10:
          chart_recom.append(chart)
    print("--- %s seconds ---" % (time.time() - start_time))
    return jsonify(chart_recom)

def onlinelearning(attributesHistory, algorithm='Momentum'):
    #make all the attributes inside the list to be 3 in size fill with None if not enough
    for i in range(len(attributesHistory)):
        if len(attributesHistory[i])<3:
            attributesHistory[i].extend(['none']*(3-len(attributesHistory[i])))

    #make the array as a pandas dataframe with index and whole attribute as a State column
    df = pd.DataFrame({'State': attributesHistory})

    df_with_actions = process_actions(df)

    if algorithm == 'Momentum':
        algo=Momentum()
        action=algo.MomentumDriver(df_with_actions)

    generator = StateGenerator('birdstrikes')
    next_state = generator.generate_next_states(df_with_actions['State'][len(df_with_actions)-1], action)

    #there are too many combinations of next states, so we will just take the first one
    next_state_filtered = list(filter(lambda x: x.lower() != 'none', next_state[0]))
    return next_state_filtered



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
            print('Reset')

        actions.append(action)

    actions.append('none')  # This is the action we want to predict
    df['Action'] = actions

    return df

if __name__ == '__main__':
    # attributesHistory= [['flight_data','wildlife_size'],['flight_data','wildlife_size','airport_name'],['flight_data','wildlife_size','airport_name']]
    # onlinelearning(attributesHistory)
    # top_k()
    app.run(port=port, debug=False)
