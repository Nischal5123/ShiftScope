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

# from gvaemodel.vis_vae import VisVAE, get_rules, get_specs
# from gvaemodel.vis_grammar import VisGrammar
from environment import environment

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
        # (_,chart)=(recommendations[chart_key])
        chart = recommendations[chart_key]
        chart_recom.append(chart)
    return jsonify(chart_recom)


#This encode2 will handle the state finding request based on what the user clicked on
@app.route('/encode2', methods=['POST'])
def encode2():
    #To-do: We need to encode the vegalite specs into one-hot vector
    specs = request.get_json()
    try:
        state = []
        # print(state)
        # env.take_step(state)
        # pdb.set_trace()
    except Exception as e:
        raise InvalidUsage(e.message)
    return jsonify(state)


@app.route('/top_k', methods=['POST'])
def top_k():
    data = request.get_json()
    if data and isinstance(data, list):
        attributes = data[0]

    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom = []
    for chart_key, _ in recommendations.items():
        # (_,chart)=(recommendations[chart_key])
        chart = recommendations[chart_key]
        chart_recom.append(chart)
    return jsonify(chart_recom)

if __name__ == '__main__':

    app.run(port=port, debug=False)