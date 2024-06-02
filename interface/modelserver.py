import json
from flask import Flask, render_template, request, jsonify, send_from_directory, current_app, session
from flask_cors import CORS
import draco_test
import pandas as pd
import time
import concurrent.futures
from environment import environment
import datetime
from performance import OnlineLearningSystem
import concurrent.futures
import pickle
import os

port = 5500
MAX_LEN = 20
app = Flask(__name__, static_folder='web/static',
            template_folder='web/templates')
CORS(app)
# Session configuration
app.secret_key = 'your_secret_key'

env = environment()
system = OnlineLearningSystem()

manual_session = {}

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
    chart_recom = system.remove_irrelevant_recommendations(field_names, recommendations)
    return jsonify(chart_recom[0])

@app.route('/get-performance-data', methods=['GET'])
def read_json_file(file_path='distribution_map.json', algorithms=['Momentum', 'Random', 'Greedy']):
    response = system.read_json_file(algorithms)

    return response

@app.route('/encode2', methods=['POST'])
def encode2():
    specs = request.get_json()
    parsed_data = json.loads(specs)

    # Extract field names from the parsed JSON
    field_names = []
    parsed_data.get('encoding', {})
    if parsed_data.get('encoding', {}) != {}:
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

    # Write to a log file the selected recommendation for current session
    with open('performance-data/selected_recommendation.txt', 'a') as f:
        # Write field names and time
        time = datetime.datetime.now()
        f.write(f'{field_names} {time}\n')
    return jsonify(specs)

def recommendation_generation(attributes):
    recommendations = draco_test.get_draco_recommendations(attributes)
    chart_recom = system.remove_irrelevant_recommendations(attributes, recommendations, max_constrained=False)
    return chart_recom

@app.route('/top_k', methods=['POST'])
def top_k(save_csv=False):
    print('Starting Recommendation Engine...')
    start_time = time.time()

    total_data = request.get_json()
    data = eval(total_data.get('history'))
    bookmarked_charts = total_data.get('bookmarked', [])
    specified_algorithm = total_data.get('algorithm', 'ActorCritic')
    specified_baseline = total_data.get('baseline', 'Momentum')

    if data and isinstance(data, list):
        system.state_history = data
    else:
        system.state_history = [['flight_date', 'wildlife_size', 'airport_name']]

    attributes_list, distribution_map, baselines_distribution_maps, attributes_baseline = system.onlinelearning(algorithms_to_run=['Momentum', 'Random', 'Greedy', 'ActorCritic', 'Qlearning'],specified_algorithm=specified_algorithm, specified_baseline=specified_baseline,bookmarked_charts=bookmarked_charts)

    chart_recom_list = []

    future_to_attributes = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        for attributes in attributes_list:
            future = executor.submit(recommendation_generation, attributes)
            future_to_attributes.append((future, attributes))

        for future, attributes in future_to_attributes:
            chart_recom = future.result()
            chart_recom_list.append(chart_recom)

    baseline_chart_recom = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as executor:
        future_to_attributes = {executor.submit(recommendation_generation, attributes): attributes for attributes in attributes_baseline}
        for future in concurrent.futures.as_completed(future_to_attributes):
            baseline_recommendations = future.result()
            baseline_chart_recom.extend(baseline_recommendations)

    response_data = {
        "chart_recommendations": chart_recom_list,
        "distribution_map": distribution_map,
        "baseline_chart_recommendations": baseline_chart_recom,
    }

    for algo, base_distribution_map in baselines_distribution_maps.items():
        with open(f'performance-data/{algo}_distribution_map.json', 'w') as f:
            json.dump(base_distribution_map, f)

    with open('performance-data/distribution_map.json', 'w') as file:
        json.dump(distribution_map, file)

    if save_csv:
        distribution_map_dataframe = pd.DataFrame.from_dict(distribution_map, orient='index', columns=['Probability'])
        distribution_map_dataframe.index.name = 'Fields'
        pd.DataFrame.to_csv(distribution_map_dataframe, 'performance-data/distribution_map.csv')

    return jsonify(response_data)

@app.route('/')
def index():
    global manual_session


    session['session_id'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    manual_session['session_id'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return jsonify(manual_session)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    global manual_session
    global system
    global env



    folder_name = 'ShiftScopeLogs/' + str(manual_session.get('session_id'))

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    save_path = 'ShiftScopeLogs/' + str(manual_session.get('session_id')) + '/'

    all_data = request.get_json()
    taskanswers = all_data.get('taskanswers')
    chartdata = all_data.get('chartdata')
    interactionlogs = all_data.get('interactionlogs')

    chartdata['bookmarked_charts'] = clean_chart_logs(chartdata['bookmarked_charts'])
    chartdata['allrecommendedcharts'] = clean_chart_logs(chartdata['allrecommendedcharts'])

    with open(save_path + 'task_answer.json', 'w') as f:
        json.dump(taskanswers, f)

    with open(save_path + 'chart_data.json', 'w') as f:
        json.dump(chartdata, f)

    with open(save_path + 'interaction_logs.json', 'w') as f:
        json.dump(interactionlogs, f)

    with open(save_path + 'online_learning_models.pkl', 'wb') as f:
        pickle.dump(system, f)

    session.clear()
    manual_session = {}
    system = OnlineLearningSystem()
    env=environment()



    return jsonify({'message': 'Form submitted successfully. New session started.'})


def clean_chart_logs(chartList):
    trimmed_chartdata = {}
    for chart in chartList:
        chart_specs = chart.get('originalspec', {})
        trimmed_chartdata[chart.get('chid', '0')] = {'encoding': chart_specs.get('encoding', {}),
                                                     'mark': chart_specs.get('mark', {})}
    return trimmed_chartdata

if __name__ == '__main__':
    app.run(port=5500, debug=True)
