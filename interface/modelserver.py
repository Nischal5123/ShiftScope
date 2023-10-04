import json
from collections import Counter
import re
from multiprocessing import Pool
from scipy.optimize import minimize
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
from sklearn.manifold import MDS, smacof
from flask import Flask, jsonify, request
from flask_cors import CORS
import pdb

from gvaemodel.vis_vae import VisVAE, get_rules, get_specs
from gvaemodel.vis_grammar import VisGrammar
from environment import environment

############# Bayesian Learning #############
import sys

sys.path.append("../implementation/")
import numpy as np
import pandas as pd
import time
from bayesian_learning import CompetingModels
import warnings

warnings.filterwarnings("ignore")
############# Bayesian Learning #############

port = 5500
rulesfile = "./gvaemodel/rules-cfg.txt"
modelsave = "./gvaemodel/vae_H256_D256_C444_333_L20_B200.hdf5"
m = re.search(r"_L(\d+)_", modelsave)

MAX_LEN = 20
LATENT = int(m.group(1))


visvae = None
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
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/encode", methods=["POST"])
def encode():
    specs = request.get_json()
    # for s in specs:
    #     #state = visvae.encode2(s)
    #     print(state)
    #     env.take_step(state)
    try:
        # tf.keras.backend.set_session(sess)
        z = visvae.encode(specs)
    except Exception as e:
        raise InvalidUsage(e.message)

    return jsonify(z.tolist())


@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Make predictions using Bayesian learning
        print(f" Bayesian model prediction start {time.time()}")
        probability_of_next_point = bayesian_learning.predict()
        print(f" Bayesian model prediction end {time.time()}")

        # Retrieve data for the top 3 predicted points
        top_indices = probability_of_next_point.nlargest(3).index.values
        data = underlying_data.loc[top_indices]

        # Prepare prediction data
        prediction = []

        # Extract 'x_attribute' and 'y_attribute' columns only once
        x_attributes = data["x_attribute"].values
        y_attributes = data["y_attribute"].values

        for x_attribute, y_attribute in zip(x_attributes, y_attributes):
            # Build prediction for 'x_attribute'
            prediction.append([x_attribute] + field_mapping[x_attribute])

            # Build prediction for 'y_attribute'
            prediction.append([y_attribute] + field_mapping[y_attribute])

        # Count occurrences of sublists
        count_dict = Counter(tuple(sublist) for sublist in prediction)

        # Create a new list with counts
        new_list = [[*sublist, count_dict[tuple(sublist)]] for sublist in prediction]

        # Remove duplicates by converting to a set and back to a list
        prediction = list({tuple(sublist): sublist for sublist in new_list}.values())

        # Print the prediction for debugging purposes
        print(prediction)
    except Exception as e:
        # Handle exceptions and provide an appropriate response
        raise InvalidUsage(str(e))

    return jsonify(prediction)


# This encode2 will handle the state finding request based on what the user clicked on
@app.route("/encode2", methods=["POST"])
def encode2():
    specs = request.get_json()
    try:
        state = visvae.encode2(specs)

        vglstr, attributes, interaction = get_vglstr_from_vgl(specs)
        index = find_interaction_id(interaction)
        print(f" Bayesian model update start {time.time()}")
        bayesian_learning.update(index)
        print(f" Bayesian model update end {time.time()}")

        print(state)
        env.take_step(state)
        # bayesian_learning.update(328)
        pdb.set_trace()

    except Exception as e:
        raise InvalidUsage(e.message)
    return jsonify(state.tolist())


def find_interaction_id(interaction):
    try:
        # Search for the index based on criteria
        index = underlying_data.loc[
            (underlying_data["mark"] == interaction[0])
            & (underlying_data["x_attribute"] == interaction[1])
            & (underlying_data["y_attribute"] == interaction[2])
        ].index[0]
    except IndexError:
        # Handle the case where no match is found
        index = 348
    return index


@app.route("/decode", methods=["POST"])
def decode():
    z = np.array(request.get_json())
    # print(z)
    try:
        # tf.keras.backend.set_session(sess)
        specs = visvae.decode(z)
        # print(specs)
    except Exception as e:
        raise InvalidUsage(e.message)
    return jsonify(specs)


@app.route("/orientate", methods=["POST"])
def orientate():
    locations = request.get_json()
    mt1, mt2, disparity = procrustes(locations[0], locations[1])
    return jsonify(mt2.tolist())


@app.route("/pca", methods=["POST"])
def pcaproject():
    global pca
    pca = PCA(n_components=2)
    x = np.array(request.get_json())
    y = pca.fit_transform(x)
    return jsonify(y.tolist())


@app.route("/invpca", methods=["POST"])
def invpcaproject():
    global pca
    y = np.array(request.get_json())
    x = pca.inverse_transform(y)
    return jsonify(x.tolist())


@app.route("/mds", methods=["POST"])
def mdsproject():
    distm = np.array(request.get_json())
    mds = MDS(
        n_components=2,
        dissimilarity="precomputed",
        random_state=13,
        max_iter=3000,
        eps=1e-9,
    )
    y = mds.fit(distm).embedding_
    # res = smacof(distm, n_components=2, random_state=13, max_iter=3000, eps=1e-9)
    # y = res[0]
    return jsonify(y.tolist())


@app.route("/invmds", methods=["POST"])
def invmdsproject():
    inputdata = request.get_json()
    ps = np.array(inputdata["points"])
    dsall = np.array(inputdata["distances"])

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
    res = minimize(objfun, x0, args=(ps, ds), tol=1e-9, options={"maxiter": 3000})
    return res.x


def objfun(x, ps, ds):
    d = np.tile(x, (ps.shape[0], 1)) - ps
    d = np.sum(np.square(d), axis=1)
    diff = np.sqrt(d) - ds
    return np.sum(np.square(diff))


def get_vglstr_from_vgl(vgl):
    # Initialize variables
    vglstr = ""
    vgl = json.loads(vgl)
    x_and_y = []
    encoding_arr = []
    all_attributes = []

    # Extract 'mark' from vgl
    vglstr += "mark:" + vgl["mark"] + ";"

    # Iterate through 'encoding' in vgl
    for encoding in vgl["encoding"]:
        attributes = []

        # Skip 'undefined' and 'size' encodings
        if encoding in {"undefined", "size"}:
            continue

        encoding_str = ""

        # Extract 'field' if available
        if "field" in vgl["encoding"][encoding]:
            field = vgl["encoding"][encoding]["field"]
            encoding_str += field + "-"
            attributes.append(field)
            x_and_y.append(field)
        else:
            encoding_str += "-"

        # Determine data type and add it to attributes
        data_type = (
            "num" if vgl["encoding"][encoding]["type"] == "quantitative" else "str"
        )
        attributes.append(data_type)
        encoding_str += vgl["encoding"][encoding]["type"] + "-"

        # Add 'encoding' type to encoding_str
        encoding_str += encoding

        # Add 'aggregate' if available
        if "aggregate" in vgl["encoding"][encoding]:
            aggregate = vgl["encoding"][encoding]["aggregate"]
            encoding_str += "<" + "aggregate" + ">" + aggregate

        # Add 'bin' if available
        if "bin" in vgl["encoding"][encoding]:
            encoding_str += "<" + "bin" + ">"

        encoding_arr.append(encoding_str)
        all_attributes.append(attributes)

    # Sort encoding_arr and build vglstr
    encoding_arr.sort()
    vglstr += "encoding:" + ",".join(encoding_arr)

    # Get unique x_and_y values and limit to the first 3
    x_and_y = list(set(x_and_y))
    x_and_y.insert(0, vgl["mark"])

    return vglstr, all_attributes, x_and_y[:3]


def processchartdata():
    return None


if __name__ == "__main__":
    rules = []
    mapping = [
        ["Title", "str", "nominal"],
        ["US_Gross", "num", "quantitative"],
        ["Worldwide_Gross", "num", "quantitative"],
        ["US_DVD_Sales", "num", "quantitative"],
        ["Production_Budget", "num", "quantitative"],
        ["Release_Date", "str", "nominal"],
        ["MPAA_Rating", "str", "nominal"],
        ["Running_Time_min", "num", "quantitative"],
        ["Distributor", "str", "nominal"],
        ["Source", "str", "nominal"],
        ["Major_Genre", "str", "nominal"],
        ["Creative_Type", "str", "nominal"],
        ["Director", "str", "nominal"],
        ["Rotten_Tomatoes_Rating", "num", "quantitative"],
        ["IMDB_Rating", "num", "quantitative"],
        ["IMDB_Votes", "num", "quantitative"],
    ]
    field_mapping = {attr[0]: [attr[1], attr[2]] for attr in mapping}
    underlying_data = pd.read_csv("../data/zheng/combinations.csv")
    underlying_data.set_index("id", drop=True, inplace=True)
    d_attrs = ["mark", "x_attribute", "y_attribute"]
    with open(rulesfile, "r") as inputs:
        for line in inputs:
            line = line.strip()
            rules.append(line)

    visvae = VisVAE(modelsave, rules, MAX_LEN, LATENT)

    pca = PCA(n_components=2)

    bayesian_learning = CompetingModels(underlying_data, [], d_attrs)

    app.run(port=port, debug=False)
