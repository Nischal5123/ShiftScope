# Define a function to run each algorithm

import random
import numpy as np
from Q_Learning import Rl_Driver
from Momentum import Momentum
import os
import json
from collections import Counter

def run_algorithm(algorithm, attributes_history, generator, dataset):
    if algorithm == 'Qlearning':
        # Save the attribute history to a numpy file
        Rl_attributesHistory = attributes_history.copy()
        # Make all the attributes inside the list to be 3 in size, fill with 'none' if not enough
        for i in range(len(Rl_attributesHistory)):
            if len(Rl_attributesHistory[i]) < 3:
                Rl_attributesHistory[i].extend(['none'] * (3 - len(Rl_attributesHistory[i])))
            elif len(Rl_attributesHistory[i]) > 3:
                Rl_attributesHistory[i] = Rl_attributesHistory[i][:3]

        # Remove the existing file if it exists
        if os.path.exists("attributes_history.npy"):
            os.remove("attributes_history.npy")

        # Save the new attribute history to a numpy file
        np.save("attributes_history.npy", np.array(Rl_attributesHistory))

        next_state_rl = Rl_Driver(dataset=dataset, attributes_history_path="attributes_history.npy", current_state=Rl_attributesHistory[-1], epsilon=0.9)
        return list(filter(lambda x: x.lower() != 'none', next_state_rl))

    elif algorithm == 'Momentum':
        # algo=Momentum()
        # action=algo.MomentumDriver(df_with_actions)
        if len(attributes_history) > 1:
            return list(filter(lambda x: x.lower() != 'none', attributes_history[-2]))
        else:
            return []

    elif algorithm == 'Greedy':
        return list(filter(lambda x: x.lower() != 'none', attributes_history[-1]))

    elif algorithm == 'Random':
        return list(filter(lambda x: x.lower() != 'none', random.choice(generator.generate_independent_next_states())))



def check_fields(dictionary, fields):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            if not check_fields(value, fields):  # Modify this line
                return False  # Modify this line
        elif key not in fields and value not in fields:  # Modify this line
            return False
    return True  # Modify this line


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


def full_version_remove_irrelevant_reccomendations(interested_attributes, recommendations, max_constrained=True):
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



# This is for Zeng et al. (2019) [1]

#
# bs_fields_uppercase={
#     'airport_name': 'Airport_Name',
#     'aircraft_make_model': 'Aircraft_Make_Model',
#     'effect_amount_of_damage': 'Effect_Amount_of_damage',
#     'flight_date': 'Flight_Date',
#     'aircraft_airline_operator': 'Aircraft_Airline_Operator',
#     'origin_state': 'Origin_State',
#     'when_phase_of_flight': 'When_Phase_of_flight',
#     'wildlife_size': 'Wildlife_Size',
#     'wildlife_species': 'Wildlife_Species',
#     'when_time_of_day': 'When_Time_of_day',
#     'cost_other': 'Cost_Other',
#     'cost_repair': 'Cost_Repair',
#     'cost_total_a': 'Cost_Total',
#     'speed_ias_in_knots': 'Speed_IAS_in_knots',
#     'none': 'none'
# }
#
#
# @app.route('/encodetest', methods=['POST'])
# def encodetest():
#     specs = request.get_json()
#     parsed_data = [json.loads(item) for item in specs]
#
#     # Extract field names and types from the parsed JSON
#     field_names = []
#     encoding_channels = []
#     field_types = {}
#     for item in parsed_data:
#         marks = [item.get('mark', 'bar')]
#         encodings = item.get('encoding', {})
#         for key in encodings:
#             encoding_channels.append(key)
#             field_info = encodings[key]
#             field_name = field_info.get('field')
#             if field_name:
#                 field_names.append(field_name)
#                 field_types[field_name] = key
#     encode_history.append(field_names)
#     # Get Draco recommendations
#     #recommendations = draco_test.get_draco_recommendations(field_names, 'birdstrikes', parsed_data)
#     uppercase_fields = [bs_fields_uppercase[field] for field in field_names]
#     request_data = {
#         "data": json.dumps({
#             "fields": uppercase_fields,
#             "version": "bdf"
#         })
#     }
#     recommendations = perform_snd_flds(request_data)
#     return jsonify(recommendations[0])
#
#
#
# @app.route('/top_k_test', methods=['POST'])
# def top_k_test(save_csv=False):
#     print('Starting Recommendation Engine...')
#     #get running time in console
#     start_time = time.time()
#
#     total_data = request.get_json()
#     data = eval(total_data.get('history'))
#
#     bookmarked_charts = total_data.get('bookmarked', [])
#     specified_algorithm = total_data.get('algorithm', 'Qlearning')
#
#     if data and isinstance(data, list):
#         attributesHistory = [[bs_fields_uppercase.get(a, a) for a in sublist] for sublist in data]
#     else:
#         attributesHistory = [['flight_data', 'wildlife_size'], ['flight_data', 'wildlife_size', 'airport_name'],
#                          ['flight_data', 'wildlife_size', 'airport_name']]
#
#     print('Attribute History', attributesHistory)
#     attributes,distribution_map,baselines_distribution_maps=onlinelearning(attributesHistory, algorithms_to_run=['Momentum','Random','Greedy','Qlearning'], specified_algorithm=specified_algorithm)
#
#     print('Requesting Encodings...', '--- %s seconds ---' % (time.time() - start_time), 'Algorithm:', specified_algorithm)
#
#     # recommendations = draco_test.get_draco_recommendations(attributes)
#     # chart_recom=remove_irrelevant_reccomendations(attributes, recommendations, max_constrained=False)
#     #dotn consider none in attributes
#     attrs = [attr for attr in attributes if attr != 'none']
#     uppercase_fields = [bs_fields_uppercase[f] for f in attrs]
#     request_data = {
#         "data": json.dumps({
#             "fields": uppercase_fields,
#             "version": "bdf"
#         })
#     }
#     # draco_recommendations = draco_test.get_draco_recommendations(attributes)
#     # chart_recom_draco = remove_irrelevant_reccomendations(attributes, draco_recommendations, max_constrained=False)
#     recommendations = perform_snd_flds(request_data)
#     # Assuming recommendations is your list of dictionaries
#     inner_dict = recommendations[0][list(recommendations[0].keys())[0]]
#     # Convert the inner dictionary to a JSON-like string with newline characters
#     json_str = json.dumps(inner_dict, indent=4)
#     chart_recom= [json_str]
#
#
#
#     print(' Recommendations Finished...', "--- %s seconds ---" % (time.time() - start_time))
#     print('Recommendation Size:', len(chart_recom))
#
#     response_data = {
#         "chart_recommendations": chart_recom,
#         "distribution_map": distribution_map
#     }
#
#     for algo, base_distribution_map in baselines_distribution_maps.items():
#         with open(f'{algo}_distribution_map.json', 'w') as f:
#             json.dump(base_distribution_map, f)
#
#     with open('distribution_map.json', 'w') as file:
#         json.dump(distribution_map, file)
#
#     if save_csv:
#         distribution_map_dataframe = pd.DataFrame.from_dict(distribution_map, orient='index', columns=['Probability'])
#         distribution_map_dataframe.index.name = 'Fields'
#         pd.DataFrame.to_csv(distribution_map_dataframe, 'distribution_map.csv')
#     return jsonify(response_data)
