import json
import os
import sys
import re
from multiprocessing import Pool
import nltk
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import procrustes
import h5py

import tensorflow as tf
from tensorflow.keras import backend as K
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, smacof
from flask import Flask, jsonify, request
from flask_cors import CORS
import pdb

from gvaemodel.vis_vae import VisVAE, get_rules, get_specs
from gvaemodel.vis_grammar import VisGrammar
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
    for s in specs:
        state = visvae.encode2(s)
        print(state)
        env.take_step(state)
    try:
        #tf.keras.backend.set_session(sess)
        z = visvae.encode(specs)
        # pdb.set_trace()
    except Exception as e:
        raise InvalidUsage(e.message)
        env.save_to_csv('environment_data.csv')
    return jsonify(z.tolist())


#This encode2 will handle the state finding request based on what the user clicked on
@app.route('/encode2', methods=['POST'])
def encode2():
    specs = request.get_json()
    try:
        state = visvae.encode2(specs)
        print(state)
        env.take_step(state)
        pdb.set_trace()
    except Exception as e:
        raise InvalidUsage(e.message)
        env.save_to_csv('environment_data.csv')
    return jsonify(state.tolist())


@app.route('/decode', methods=['POST'])
def decode():
    z = np.array(request.get_json())
    # print(z)
    try:
        #tf.keras.backend.set_session(sess)
        specs = visvae.decode(z)
        # print(specs)
    except Exception as e:
        raise InvalidUsage(e.message)
        env.save_to_csv('environment_data.csv')
    return jsonify(specs)


@app.route('/orientate', methods=['POST'])
def orientate():
    locations = request.get_json()
    mt1, mt2, disparity = procrustes(locations[0], locations[1])
    return jsonify(mt2.tolist())


@app.route('/pca', methods=['POST'])
def pcaproject():
    global pca
    pca = PCA(n_components=2)
    x = np.array(request.get_json())
    y = pca.fit_transform(x)
    return jsonify(y.tolist())


@app.route('/invpca', methods=['POST'])
def invpcaproject():
    global pca
    y = np.array(request.get_json())
    x = pca.inverse_transform(y)
    return jsonify(x.tolist())


@app.route('/mds', methods=['POST'])
def mdsproject():
    distm = np.array(request.get_json())
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=13, max_iter=3000, eps=1e-9)
    y = mds.fit(distm).embedding_
    # res = smacof(distm, n_components=2, random_state=13, max_iter=3000, eps=1e-9)
    # y = res[0]
    return jsonify(y.tolist())


@app.route('/invmds', methods=['POST'])
def invmdsproject():
    inputdata = request.get_json()
    ps = np.array(inputdata['points'])
    dsall = np.array(inputdata['distances'])

    # res = myminimize((ps, dsall[0]))
    pool = Pool(8)
    res = pool.map(myminimize, [(ps, ds) for ds in dsall])
    res = [r.tolist() for r in res]
    pool.close()
    pool.join()
    return jsonify(res)


def myminimize(args):
    ps, ds = args
    x0 = np.random.random_sample(ps[0].shape)
    res = minimize(objfun, x0, args=(ps, ds), tol=1e-9, options={'maxiter': 3000})
    return res.x


def objfun(x, ps, ds):
    d = np.tile(x, (ps.shape[0], 1)) - ps
    d = np.sum(np.square(d), axis=1)
    diff = np.sqrt(d) - ds
    return np.sum(np.square(diff))


if __name__ == '__main__':
    rules = []
    with open(rulesfile, 'r') as inputs:
        for line in inputs:
            line = line.strip()
            rules.append(line)


    visvae = VisVAE(modelsave, rules, MAX_LEN, LATENT)


    pca = PCA(n_components=2)

    app.run(port=port, debug=False)